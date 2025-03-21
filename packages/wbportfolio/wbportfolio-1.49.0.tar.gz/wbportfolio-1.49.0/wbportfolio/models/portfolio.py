import logging
from collections import defaultdict
from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal
from math import isclose
from typing import Any, Iterable

import numpy as np
import pandas as pd
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    Exists,
    F,
    OuterRef,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from pandas._libs.tslibs.offsets import BDay
from skfolio.preprocessing import prices_to_returns
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.models import WBModel
from wbcore.utils.importlib import import_from_dotted_path
from wbcore.utils.models import ActiveObjectManager, DeleteToDisableMixin
from wbfdm.contrib.metric.tasks import compute_metrics_as_task
from wbfdm.models import Instrument, InstrumentType
from wbfdm.models.instruments.instrument_prices import InstrumentPrice
from wbfdm.signals import investable_universe_updated

from wbportfolio.models.asset import AssetPosition
from wbportfolio.models.indexes import Index
from wbportfolio.models.portfolio_relationship import (
    InstrumentPortfolioThroughModel,
    PortfolioInstrumentPreferredClassificationThroughModel,
)
from wbportfolio.models.products import Product
from wbportfolio.pms.analytics.portfolio import Portfolio as AnalyticPortfolio
from wbportfolio.pms.typing import Portfolio as PortfolioDTO

from . import ProductGroup
from .exceptions import InvalidAnalyticPortfolio

logger = logging.getLogger("pms")


class PositionDictConverter:
    """Utility class to load a dictionary of dictionary (dictionary of instrument_id and float per date) into a iterable of assetposition"""

    def __init__(self, portfolio, prices: pd.DataFrame, infer_underlying_quote_price=False):
        self.portfolio = portfolio
        self.instruments = {}
        self.fx_rates = defaultdict(dict)
        self.prices = prices
        self.infer_underlying_quote_price = infer_underlying_quote_price

    def _get_instrument(self, instrument_id: int) -> Instrument:
        try:
            return self.instruments[instrument_id]
        except KeyError:
            instrument = Instrument.objects.get(id=instrument_id)
            self.instruments[instrument_id] = instrument
            return instrument

    def _get_fx_rate(self, val_date: date, currency) -> CurrencyFXRates:
        try:
            return self.fx_rates[currency][val_date]
        except KeyError:
            fx_rate = CurrencyFXRates.objects.get_or_create(
                currency=currency, date=val_date, defaults={"value": Decimal(0)}
            )[0]  # we create a fx rate anyway to not fail the position. The fx rate expect to be there later on
            self.fx_rates[currency][val_date] = fx_rate
            return fx_rate

    def dict_to_model(self, val_date: date, instrument_id: int, weighting: float) -> AssetPosition | None:
        underlying_quote = self._get_instrument(instrument_id)
        currency_fx_rate_portfolio_to_usd = self._get_fx_rate(val_date, self.portfolio.currency)
        currency_fx_rate_instrument_to_usd = self._get_fx_rate(val_date, underlying_quote.currency)
        initial_price = self.prices.loc[pd.Timestamp(val_date), instrument_id]
        # if we cannot find a price for the instrument, we return an empty position
        if initial_price is not None:
            position = AssetPosition(
                underlying_quote=underlying_quote,
                weighting=weighting,
                date=val_date,
                asset_valuation_date=val_date,
                is_estimated=True,
                portfolio=self.portfolio,
                currency=underlying_quote.currency,
                initial_price=self.prices.loc[pd.Timestamp(val_date), instrument_id],
                currency_fx_rate_portfolio_to_usd=currency_fx_rate_portfolio_to_usd,
                currency_fx_rate_instrument_to_usd=currency_fx_rate_instrument_to_usd,
                initial_currency_fx_rate=None,
                underlying_quote_price=None,
                underlying_instrument=None,
            )
            position.pre_save(
                infer_underlying_quote_price=self.infer_underlying_quote_price
            )  # inferring underlying quote price is potentially very slow for big dataset of positions, it's not very needed for model portfolio so we disable it
            return position

    def convert(self, positions: dict[date, dict[int, float]]) -> Iterable[AssetPosition]:
        for val_date, weights in positions.items():
            yield from filter(
                lambda x: x, map(lambda row: self.dict_to_model(val_date, row[0], row[1]), weights.items())
            )


class DefaultPortfolioQueryset(QuerySet):
    def filter_invested_at_date(self, val_date: date) -> QuerySet:
        """
        Filter the queryset to get only portfolio invested at the given date
        """
        return self.filter(
            (Q(invested_timespan__startswith__lte=val_date) | Q(invested_timespan__startswith__isnull=True))
            & (Q(invested_timespan__endswith__gt=val_date) | Q(invested_timespan__endswith__isnull=True))
        )

    def filter_active_and_tracked(self):
        return self.annotate(
            has_product=Exists(
                InstrumentPortfolioThroughModel.objects.filter(
                    instrument__instrument_type=InstrumentType.PRODUCT, portfolio=OuterRef("pk")
                )
            )
        ).filter((Q(has_product=True) | Q(is_manageable=True)) & Q(is_active=True) & Q(is_tracked=True))

    def to_dependency_iterator(self, val_date: date) -> Iterable["Portfolio"]:
        """
        A method to sort the given queryset to return undependable portfolio first. This is very useful if a routine needs to be applied sequentially on portfolios by order of dependence.
        """
        MAX_ITERATIONS: int = (
            5  # in order to avoid circular dependency and infinite loop, we need to stop recursion at a max depth
        )
        remaining_portfolios = set(self)

        def _iterator(p, iterator_counter=0):
            iterator_counter += 1
            parent_portfolios = remaining_portfolios & set(
                map(lambda o: o[0], p.get_parent_portfolios(val_date))
            )  # get composition parent portfolios
            dependency_relationships = PortfolioPortfolioThroughModel.objects.filter(
                portfolio=p, dependency_portfolio__in=remaining_portfolios
            )  # get dependency portfolios
            if iterator_counter >= MAX_ITERATIONS or (
                not dependency_relationships.exists() and not bool(parent_portfolios)
            ):  # if not dependency portfolio or parent portfolio that remained, then we yield
                remaining_portfolios.remove(p)
                yield p
            else:
                # otherwise, we iterate of the dependency portfolio first
                deps_portfolios = parent_portfolios.union(
                    set([r.dependency_portfolio for r in dependency_relationships])
                )
                for deps_p in deps_portfolios:
                    yield from _iterator(deps_p, iterator_counter=iterator_counter)

        while len(remaining_portfolios) > 0:
            portfolio = next(iter(remaining_portfolios))
            yield from _iterator(portfolio)


class DefaultPortfolioManager(ActiveObjectManager):
    def get_queryset(self):
        return DefaultPortfolioQueryset(self.model).filter(is_active=True)

    def filter_invested_at_date(self, val_date: date):
        return self.get_queryset().filter_invested_at_date(val_date)

    def filter_active_and_tracked(self):
        return self.get_queryset().filter_active_and_tracked()


class ActiveTrackedPortfolioManager(DefaultPortfolioManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(asset_exists=Exists(AssetPosition.unannotated_objects.filter(portfolio=OuterRef("pk"))))
            .filter(asset_exists=True, is_tracked=True)
        )


class PortfolioPortfolioThroughModel(models.Model):
    class Type(models.TextChoices):
        PRIMARY = "PRIMARY", "Primary"
        MODEL = "MODEL", "Model"
        CUSTODIAN = "CUSTODIAN", "Custodian"

    portfolio = models.ForeignKey("wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="dependency_through")
    dependency_portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="dependent_through"
    )
    type = models.CharField(choices=Type.choices, default=Type.PRIMARY, verbose_name="Type")

    def __str__(self):
        return f"{self.portfolio} dependant on {self.dependency_portfolio} ({self.Type[self.type].label})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["portfolio", "type"], name="unique_primary", condition=Q(type="PRIMARY")),
            models.UniqueConstraint(fields=["portfolio", "type"], name="unique_model", condition=Q(type="MODEL")),
        ]


class Portfolio(DeleteToDisableMixin, WBModel):
    assets: models.QuerySet[AssetPosition]

    name = models.CharField(
        max_length=255,
        verbose_name="Name",
        default="",
        help_text="The Name of the Portfolio",
    )

    currency = models.ForeignKey(
        to="currency.Currency",
        related_name="portfolios",
        on_delete=models.PROTECT,
        verbose_name="Currency",
        help_text="The currency of the portfolio.",
    )
    hedged_currency = models.ForeignKey(
        to="currency.Currency",
        related_name="hedged_portfolios",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Hedged Currency",
        help_text="The hedged currency of the portfolio.",
    )
    depends_on = models.ManyToManyField(
        "wbportfolio.Portfolio",
        symmetrical=False,
        related_name="dependent_portfolios",
        through="wbportfolio.PortfolioPortfolioThroughModel",
        through_fields=("portfolio", "dependency_portfolio"),
        blank=True,
        verbose_name="The portfolios this portfolio depends on",
    )

    preferred_instrument_classifications = models.ManyToManyField(
        "wbfdm.Instrument",
        limit_choices_to=(models.Q(instrument_type__is_classifiable=True) & models.Q(level=0)),
        related_name="preferred_portfolio_classifications",
        through="wbportfolio.PortfolioInstrumentPreferredClassificationThroughModel",
        through_fields=("portfolio", "instrument"),
        blank=True,
        verbose_name="The Preferred classification per instrument",
    )
    instruments = models.ManyToManyField(
        "wbfdm.Instrument",
        through=InstrumentPortfolioThroughModel,
        related_name="portfolios",
        blank=True,
        verbose_name="Instruments",
        help_text="Instruments linked to this instrument",
    )
    invested_timespan = DateRangeField(
        null=True, blank=True, help_text="Define when this portfolio is considered invested"
    )

    is_manageable = models.BooleanField(
        default=False,
        help_text="True if the portfolio can be manually modified (e.g. Trade proposal be submitted or total weight recomputed)",
    )
    is_tracked = models.BooleanField(
        default=True,
        help_text="True if the internal updating mechanism (e.g., Next weights or Look-Through computation, rebalancing etc...) needs to apply to this portfolio",
    )
    only_weighting = models.BooleanField(
        default=False,
        help_text="Indicates that this portfolio is only utilizing weights and disregards shares, e.g. a model portfolio",
    )
    is_lookthrough = models.BooleanField(
        default=False,
        help_text="Indicates that this portfolio is a look-through portfolio",
    )
    is_composition = models.BooleanField(
        default=False, help_text="If true, this portfolio is a composition of other portfolio"
    )
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name="Updated At")
    last_position_date = models.DateField(blank=True, null=True, verbose_name="Last Position Date")
    initial_position_date = models.DateField(blank=True, null=True, verbose_name="Last Position Date")

    bank_accounts = models.ManyToManyField(
        to="directory.BankingContact",
        related_name="wbportfolio_portfolios",
        through="wbportfolio.PortfolioBankAccountThroughModel",
        blank=True,
    )

    objects = DefaultPortfolioManager()
    tracked_objects = ActiveTrackedPortfolioManager()

    @property
    def primary_portfolio(self):
        with suppress(PortfolioPortfolioThroughModel.DoesNotExist):
            return PortfolioPortfolioThroughModel.objects.get(
                portfolio=self, type=PortfolioPortfolioThroughModel.Type.PRIMARY
            ).dependency_portfolio

    @property
    def model_portfolio(self):
        with suppress(PortfolioPortfolioThroughModel.DoesNotExist):
            return PortfolioPortfolioThroughModel.objects.get(
                portfolio=self, type=PortfolioPortfolioThroughModel.Type.MODEL
            ).dependency_portfolio

    @property
    def composition_portfolio(self):
        with suppress(PortfolioPortfolioThroughModel.DoesNotExist):
            return PortfolioPortfolioThroughModel.objects.get(
                portfolio=self,
                type=PortfolioPortfolioThroughModel.Type.MODEL,
                dependency_portfolio__is_composition=True,
            ).dependency_portfolio

    @property
    def imported_assets(self):
        return self.assets.filter(is_estimated=False)

    @cached_property
    def pms_instruments(self):
        instruments = [i for i in Product.objects.filter(portfolios=self)]
        instruments.extend([i for i in ProductGroup.objects.filter(portfolios=self)])
        instruments.extend([i for i in Index.objects.filter(portfolios=self)])
        return instruments

    @property
    def can_be_rebalanced(self):
        return self.is_tracked and self.is_manageable and not self.is_lookthrough

    def delete(self, **kwargs):
        super().delete(**kwargs)
        # We check if for all linked instruments, this portfolio was the last active one (if yes, we disable the instrument)
        if self.id:
            for instrument in self.instruments.iterator():
                if not instrument.portfolios.filter(is_active=True).exists():
                    instrument.delisted_date = date.today() - timedelta(days=1)
                    instrument.save()

    def _build_dto(self, val_date: date, **extra_kwargs) -> PortfolioDTO:
        "returns the dto representation of this portfolio at the specified date"
        return PortfolioDTO(
            tuple([pos._build_dto() for pos in self.assets.filter(date=val_date, **extra_kwargs)]),
        )

    def get_weights(self, val_date: date) -> dict[int, float]:
        """
        A convenience utility method to returns the portfolio weights for this portfolio as a dictionary (instrument id as key and weights as value)

        Args:
            val_date: The date at which to return the weights for this portfolio

        Returns:
            A dictionary containing the weights for this portfolio
        """
        return dict(
            map(
                lambda r: (r[0], float(r[1])),
                self.assets.filter(date=val_date)
                .values("underlying_quote")
                .annotate(sum_weight=Sum("weighting"))
                .values_list("underlying_quote", "sum_weight"),
            )
        )

    def get_analytic_portfolio(self, val_date: date, **kwargs) -> tuple[AnalyticPortfolio, pd.DataFrame]:
        """
        Return the analytic portfolio associated with this portfolio at the given date

        the analytic portfolio inherit from SKFolio Portfolio and can be used to access all this library methods
        Args:
            val_date: the date to calculate the portfolio for

        Returns:
            The instantiated analytic portfolio
        """
        weights = self.get_weights(val_date)
        return_date = (val_date + BDay(1)).date()
        returns, prices = self.get_returns((val_date - BDay(2)).date(), return_date, **kwargs)
        if pd.Timestamp(return_date) not in returns.index:
            raise InvalidAnalyticPortfolio()
        returns = returns.fillna(0)  # not sure this is what we want
        return (
            AnalyticPortfolio(
                X=returns,
                weights=weights,
            ),
            prices,
        )

    def is_invested_at_date(self, val_date: date) -> bool:
        return (
            self.invested_timespan
            and self.invested_timespan.upper > val_date
            and self.invested_timespan.lower <= val_date
        )

    def __str__(self):
        return f"{self.id:06} ({self.name})"

    class Meta:
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

        notification_types = [
            create_notification_type(
                "wbportfolio.portfolio.check_custodian_portfolio",
                "Check Custodian Portfolio",
                "Sends a notification when a portfolio does not match with its custodian portfolio",
                True,
                True,
                True,
            ),
        ]

    def is_active_at_date(self, val_date: date) -> bool:
        """
        Return if the base instrument has a total aum greater than 0
        :val_date: the date at which we need to evaluate if the portfolio is considered active
        """
        active_portfolio = self.is_active or self.deletion_datetime.date() > val_date
        if self.instruments.exists():
            return active_portfolio and any(
                [instrument.is_active_at_date(val_date) for instrument in self.instruments.all()]
            )
        return active_portfolio

    def get_total_asset_value(self, val_date: date) -> Decimal:
        """
        Return the total asset under management of the portfolio at the specified valuation date
        Args:
            val_date: The date at which aum needs to be computed
        Returns:
            The total AUM (0 if there is no position)
        """
        return self.assets.filter(date=val_date).aggregate(s=Sum("total_value_fx_portfolio"))["s"] or Decimal(0.0)

    def get_total_asset_under_management(self, val_date):
        from wbportfolio.models.transactions.trades import Trade

        trades = Trade.valid_customer_trade_objects.filter(portfolio=self, transaction_date__lte=val_date)

        total_aum = Decimal(0)
        for underlying_instrument_id, sum_shares in (
            trades.values("underlying_instrument")
            .annotate(
                sum_shares=Sum("shares"),
            )
            .values_list("underlying_instrument", "sum_shares")
        ):
            with suppress(Instrument.DoesNotExist, InstrumentPrice.DoesNotExist):
                instrument = Instrument.objects.get(id=underlying_instrument_id)
                last_price = instrument.valuations.filter(date__lte=val_date).latest("date").net_value
                fx_rate = instrument.currency.convert(val_date, self.currency)
                total_aum += last_price * sum_shares * fx_rate
        return total_aum

    def _get_assets(self, with_estimated=True, with_cash=True):
        qs = self.assets
        if not with_estimated:
            qs = qs.filter(is_estimated=False)
        if not with_cash:
            qs = qs.exclude(underlying_instrument__is_cash=True)
        return qs

    def get_earliest_asset_position_date(self, val_date=None, with_estimated=False):
        qs = self._get_assets(with_estimated=with_estimated)
        if val_date:
            qs = qs.filter(date__gte=val_date)
        if qs.exists():
            return qs.earliest("date").date
        return None

    def get_latest_asset_position_date(self, val_date=None, with_estimated=False):
        qs = self._get_assets(with_estimated=with_estimated)
        if val_date:
            qs = qs.filter(date__lte=val_date)

        if qs.exists():
            return qs.latest("date").date
        return None

    # Asset Position Utility Functions
    def get_holding(self, val_date, exclude_cash=True, exclude_index=True):
        qs = self._get_assets(with_cash=not exclude_cash).filter(date=val_date, weighting__gt=0)
        if exclude_index:
            qs = qs.exclude(underlying_instrument__instrument_type=InstrumentType.INDEX)
        return (
            qs.values("underlying_instrument__name")
            .annotate(total_value_fx_portfolio=Sum("total_value_fx_portfolio"), weighting=Sum("weighting"))
            .order_by("-total_value_fx_portfolio")
        )

    def _get_groupedby_df(
        self,
        group_by,
        val_date: date,
        exclude_cash: bool | None = False,
        exclude_index: bool | None = False,
        extra_filter_parameters: dict[str, Any] = None,
        **groupby_kwargs,
    ):
        qs = self._get_assets(with_cash=not exclude_cash).filter(date=val_date)
        if exclude_index:
            # We exclude only index that are not considered as cash. Setting exclude_cash to true convers this case.
            qs = qs.exclude(
                Q(underlying_instrument__instrument_type=InstrumentType.INDEX)
                & Q(underlying_instrument__is_cash=False)
            )
        if extra_filter_parameters:
            qs = qs.filter(**extra_filter_parameters)
        qs = group_by(qs, **groupby_kwargs).annotate(sum_weighting=Sum(F("weighting"))).order_by("-sum_weighting")
        df = pd.DataFrame(
            qs.values_list("aggregated_title", "sum_weighting"), columns=["aggregated_title", "weighting"]
        )
        if not df.empty:
            df.weighting = df.weighting.astype("float")
            df.weighting = df.weighting / df.weighting.sum()
            df = df.sort_values(by=["weighting"])
        return df.where(pd.notnull(df), None)

    def get_geographical_breakdown(self, val_date, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.country_group_by, val_date=val_date, exclude_cash=True, exclude_index=True, **kwargs
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_currency_exposure(self, val_date, **kwargs):
        df = self._get_groupedby_df(AssetPosition.currency_group_by, val_date=val_date, **kwargs)
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_equity_market_cap_distribution(self, val_date, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.marketcap_group_by,
            val_date=val_date,
            exclude_cash=True,
            exclude_index=True,
            extra_filter_parameters={"underlying_instrument__instrument_type": InstrumentType.EQUITY},
            **kwargs,
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_equity_liquidity(self, val_date, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.liquidity_group_by,
            val_date=val_date,
            exclude_cash=True,
            exclude_index=True,
            extra_filter_parameters={"underlying_instrument__instrument_type": InstrumentType.EQUITY},
            **kwargs,
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_industry_exposure(self, val_date=None, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.group_by_primary, val_date=val_date, exclude_cash=True, exclude_index=True, **kwargs
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_asset_allocation(self, val_date=None, **kwargs):
        df = self._get_groupedby_df(AssetPosition.cash_group_by, val_date=val_date, **kwargs)
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_adjusted_child_positions(self, val_date):
        if (
            child_positions := self.assets.exclude(underlying_instrument__is_cash=True).filter(date=val_date)
        ).count() == 1:
            if portfolio := child_positions.first().underlying_instrument.primary_portfolio:
                child_positions = portfolio.assets.exclude(underlying_instrument__is_cash=True).filter(date=val_date)
        for position in child_positions:
            if child_portfolio := position.underlying_instrument.primary_portfolio:
                index_positions = child_portfolio.assets.exclude(underlying_instrument__is_cash=True).filter(
                    date=val_date
                )

                for index_position in index_positions.all():
                    weighting = index_position.weighting * position.weighting
                    if weighting != 0:
                        yield {
                            "underlying_instrument_id": index_position.underlying_instrument.id,
                            "weighting": weighting,
                        }

    def get_longshort_distribution(self, val_date):
        df = pd.DataFrame(self.get_adjusted_child_positions(val_date))

        if not df.empty:
            df["is_cash"] = df.underlying_instrument_id.apply(lambda x: Instrument.objects.get(id=x).is_cash)
            df = df[~df["is_cash"]]
            df = (
                df[["underlying_instrument_id", "weighting"]].groupby("underlying_instrument_id").sum().astype("float")
            )
            df.weighting = df.weighting / df.weighting.sum()
            short_weight = df[df.weighting < 0].weighting.abs().sum()
            long_weight = df[df.weighting > 0].weighting.sum()
            total_weight = long_weight + short_weight
            return pd.DataFrame(
                [
                    {"title": "Long", "weighting": long_weight / total_weight},
                    {"title": "Short", "weighting": short_weight / total_weight},
                ]
            )
        return df

    def get_portfolio_contribution_df(self, start, end, with_cash=True, hedged_currency=None, only_equity=False):
        qs = self._get_assets(with_cash=with_cash).filter(date__gte=start, date__lte=end)
        if only_equity:
            qs = qs.filter(underlying_instrument__instrument_type=InstrumentType.EQUITY)
        return Portfolio.get_contribution_df(qs, hedged_currency=hedged_currency)

    def check_related_portfolio_at_date(self, val_date: date, related_portfolio: "Portfolio"):
        assets = AssetPosition.objects.filter(
            date=val_date, underlying_instrument__is_cash=False, underlying_instrument__is_cash_equivalent=False
        ).values("underlying_instrument", "shares")
        assets1 = assets.filter(portfolio=self)
        assets2 = assets.filter(portfolio=related_portfolio)
        return assets1.difference(assets2)

    def get_child_portfolios(self, val_date: date) -> set["Portfolio"]:
        child_portfolios = set()
        instrument_rel = InstrumentPortfolioThroughModel.objects.filter(portfolio=self)
        if instrument_rel.exists():
            for parent_portfolio in Portfolio.objects.filter(
                id__in=AssetPosition.unannotated_objects.filter(
                    date=val_date, underlying_quote__in=instrument_rel.values("instrument")
                ).values("portfolio")
            ):
                child_portfolios.add(parent_portfolio)
        return child_portfolios

    def get_parent_portfolios(self, val_date: date) -> set["Portfolio"]:
        for asset in self.assets.filter(date=val_date, underlying_instrument__portfolios__isnull=False).distinct(
            "underlying_instrument"
        ):
            if portfolio := asset.underlying_instrument.portfolio:
                yield portfolio, asset.weighting

    def change_at_date(
        self,
        val_date: date,
        recompute_weighting: bool = False,
        force_recompute_weighting: bool = False,
        compute_metrics: bool = False,
        evaluate_rebalancer: bool = True,
    ):
        logger.info(f"change at date for {self} at {val_date}")

        if recompute_weighting:
            # We normalize weight across the portfolio for a given date
            qs = self.assets.filter(date=val_date).filter(
                Q(total_value_fx_portfolio__isnull=False) | Q(weighting__isnull=False)
            )
            if (self.is_lookthrough or self.is_manageable or force_recompute_weighting) and qs.exists():
                total_weighting = qs.aggregate(s=Sum("weighting"))["s"]
                # We check if this actually necessary
                # (i.e. if the weight is already summed to 100%, it is already normalized)
                if (
                    not total_weighting
                    or not isclose(total_weighting, Decimal(1.0), abs_tol=0.001)
                    or force_recompute_weighting
                ):
                    total_value = qs.aggregate(s=Sum("total_value_fx_portfolio"))["s"]
                    # TODO we change this because postgres doesn't support join statement in update (and total_value_fx_portfolio is a joined annoted field)
                    for asset in qs:
                        if total_value:
                            asset.weighting = asset._total_value_fx_portfolio / total_value
                        elif total_weighting:
                            asset.weighting = asset.weighting / total_weighting
                        asset.save()

        # We check if there is an instrument attached to the portfolio with calculated NAV and price computation method
        self.estimate_net_asset_values((val_date + BDay(1)).date())  # updating weighting in t0 influence nav in t+1
        if evaluate_rebalancer:
            self.evaluate_rebalancing(val_date)

        self.updated_at = timezone.now()
        if self.assets.filter(date=val_date).exists():
            if not self.last_position_date or self.last_position_date < val_date:
                self.last_position_date = val_date
            if not self.initial_position_date or self.initial_position_date > val_date:
                self.initial_position_date = val_date
        self.save()

        if compute_metrics:
            compute_metrics_as_task.delay(
                val_date, basket_id=self.id, basket_content_type_id=ContentType.objects.get_for_model(Portfolio).id
            )
        self.handle_controlling_portfolio_change_at_date(val_date)

    def handle_controlling_portfolio_change_at_date(self, val_date: date):
        for rel in PortfolioPortfolioThroughModel.objects.filter(
            dependency_portfolio=self, type=PortfolioPortfolioThroughModel.Type.PRIMARY, portfolio__is_lookthrough=True
        ):
            portfolio_total_asset_value = (
                self.get_total_asset_under_management(val_date) if not self.only_weighting else None
            )
            rel.portfolio.compute_lookthrough(val_date, portfolio_total_asset_value=portfolio_total_asset_value)
        for rel in PortfolioPortfolioThroughModel.objects.filter(
            dependency_portfolio=self, type=PortfolioPortfolioThroughModel.Type.MODEL
        ):
            rel.portfolio.evaluate_rebalancing(val_date)
        for dependent_portfolio in self.get_child_portfolios(val_date):
            dependent_portfolio.handle_controlling_portfolio_change_at_date(val_date)

    def evaluate_rebalancing(self, val_date: date):
        if hasattr(self, "automatic_rebalancer"):
            # if the portfolio has an automatic rebalancer and the next business day is suitable with the rebalancer, we create a trade proposal automatically
            next_business_date = (val_date + BDay(1)).date()
            if self.automatic_rebalancer.is_valid(val_date):  # we evaluate the rebalancer in t0 and t+1
                logger.info(f"Evaluate Rebalancing for {self} at {val_date}")
                self.automatic_rebalancer.evaluate_rebalancing(val_date)
            if self.automatic_rebalancer.is_valid(next_business_date):
                logger.info(f"Evaluate Rebalancing for {self} at {next_business_date}")
                self.automatic_rebalancer.evaluate_rebalancing(next_business_date)

    def estimate_net_asset_values(self, val_date: date):
        for instrument in self.pms_instruments:
            if instrument.is_active_at_date(val_date) and (
                net_asset_value_computation_method_path := instrument.net_asset_value_computation_method_path
            ):
                logger.info(f"Estimate NAV of {val_date:%Y-%m-%d} for instrument {instrument}")
                net_asset_value_computation_method = import_from_dotted_path(net_asset_value_computation_method_path)
                estimated_net_asset_value = net_asset_value_computation_method(val_date, instrument)
                if estimated_net_asset_value is not None:
                    InstrumentPrice.objects.update_or_create(
                        instrument=instrument,
                        date=val_date,
                        calculated=True,
                        defaults={
                            "gross_value": estimated_net_asset_value,
                            "net_value": estimated_net_asset_value,
                        },
                    )
                    if (
                        val_date == instrument.last_price_date
                    ):  # if price date is the latest instrument price date, we recompute the last valuation data
                        instrument.update_last_valuation_date()

    def batch_portfolio(self, start_date: date, end_date: date):
        """
        Create the cumulative portfolios between the two given dates and stop at the first rebalancing (if any)

        Returns: The trade proposal generated by the rebalancing, if any (otherwise None)
        """
        rebalancer = getattr(self, "automatic_rebalancer", None)

        weights = self.get_weights(start_date)  # initial weights
        positions = dict()
        next_trade_proposal = None
        rebalancing_date = None
        logger.info(f"compute next weights in batch for {self} from {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}")
        returns, prices = self.get_returns((start_date - BDay(3)).date(), end_date, ffill_returns=True)
        for to_date_ts in pd.date_range(start_date + timedelta(days=1), end_date, freq="B"):
            to_date = to_date_ts.date()
            logger.info(f"Processing {to_date:%Y-%m-%d}")
            if rebalancer and rebalancer.is_valid(to_date):
                rebalancing_date = to_date
                break
            try:
                last_returns = returns.loc[[to_date_ts], :]
                analytic_portfolio = AnalyticPortfolio(weights=weights, X=last_returns)
                weights = analytic_portfolio.get_next_weights()
                positions[to_date] = weights
            except KeyError:  # if no return for that date, we break and continue
                break
        positions_generator = PositionDictConverter(self, prices)
        positions = list(positions_generator.convert(positions))
        self.bulk_create_positions(positions, delete_leftovers=True, compute_metrics=False, evaluate_rebalancer=False)
        if rebalancing_date:
            next_trade_proposal = rebalancer.evaluate_rebalancing(rebalancing_date)

        return next_trade_proposal

    def propagate_or_update_assets(self, from_date: date, to_date: date):
        """
        Create a new portfolio at `to_date` based on the portfolio in `from_date`.

        Args:
            from_date: The date to propagate the portfolio from
            to_date:  The date to create the new portfolio at

        """
        from_is_active = self.is_active_at_date(from_date)
        to_is_active = self.is_active_at_date(to_date)

        def _parse_position(asset: AssetPosition) -> AssetPosition:
            # function to handle the position modification after instantiation
            if from_is_active and not to_is_active:
                asset.weighting = Decimal(0.0)
            asset.initial_shares = AssetPosition.unannotated_objects.filter(
                date=from_date, underlying_quote=asset.underlying_quote, portfolio=self
            ).aggregate(sum_shares=Sum("initial_shares"))["sum_shares"]
            return asset

        # we don't propagate on already imported portfolio by default
        is_target_portfolio_imported = self.assets.filter(date=to_date, is_estimated=False).exists()
        if (
            self.is_tracked and not self.is_lookthrough and not is_target_portfolio_imported and from_is_active
        ):  # we cannot propagate a new portfolio for untracked, or look-through or already imported or inactive portfolios
            logger.info(f"computing next weight for {self} from {from_date:%Y-%m-%d} to {to_date:%Y-%m-%d}")
            with suppress(InvalidAnalyticPortfolio):
                analytic_portfolio, to_prices = self.get_analytic_portfolio(from_date)
                if not to_prices.empty:
                    weights = analytic_portfolio.get_next_weights()
                    positions_generator = PositionDictConverter(
                        self, to_prices, infer_underlying_quote_price=True
                    ).convert({to_date: weights})
                    positions = list(map(lambda a: _parse_position(a), positions_generator))
                    self.bulk_create_positions(positions, delete_leftovers=True, compute_metrics=True)

    def get_lookthrough_positions(
        self,
        sync_date: date,
        portfolio_total_asset_value: Decimal | None = None,
        with_intermediary_position: bool = False,
    ):
        """Recursively calculates the look-through position for a portfolio

        Arguments:
            sync_date {datetime.date} -- The date on which the assets will be computed
            portfolio_total_value: {Decimal} -- The total value of the portfolio (needed to compute initial shares)
        """

        def _crawl_portfolio(
            parent_portfolio,
            adjusted_weighting,
            adjusted_currency_fx_rate,
            adjusted_is_estimated,
            portfolio_created=None,
            path=None,
        ):
            if not path:
                path = []
            path.append(parent_portfolio)
            for position in parent_portfolio.assets.filter(date=sync_date):
                position.id = None
                position.weighting = adjusted_weighting * position.weighting
                position.initial_currency_fx_rate = adjusted_currency_fx_rate * position.currency_fx_rate
                position.is_estimated = (adjusted_is_estimated or position.is_estimated) and not (
                    position.weighting == 1.0
                )
                position.portfolio_created = portfolio_created
                setattr(position, "path", path)
                position.initial_shares = None
                if portfolio_total_asset_value:
                    position.initial_shares = (position.weighting * portfolio_total_asset_value) / (
                        position.price * position.currency_fx_rate
                    )
                if child_portfolio := position.underlying_quote.primary_portfolio:
                    if with_intermediary_position:
                        yield position
                    yield from _crawl_portfolio(
                        child_portfolio,
                        position.weighting,
                        position.currency_fx_rate,
                        position.is_estimated,
                        portfolio_created=child_portfolio,
                        path=path.copy(),
                    )
                elif position.weighting:  # we do not yield position with weight 0 because of issue with certain multi-thematic portfolios which contain duplicates
                    yield position

        yield from _crawl_portfolio(self, Decimal(1.0), Decimal(1.0), False)

    def get_positions(self, val_date: date, **kwargs) -> Iterable[AssetPosition]:
        if self.is_composition:
            assets = list(self.get_lookthrough_positions(val_date, **kwargs))
        else:
            assets = self.assets.filter(date=val_date)
        return assets

    def compute_lookthrough(self, sync_date: date, portfolio_total_asset_value: Decimal | None = None):
        if not self.primary_portfolio or not self.is_lookthrough:
            raise ValueError(
                "Lookthrough position can only be computed on lookthrough portfolio with a primary portfolio"
            )
        logger.info(f"Compute Look-Through for {self} at {sync_date}")
        positions = self.primary_portfolio.get_lookthrough_positions(sync_date, portfolio_total_asset_value)
        self.bulk_create_positions(list(positions), delete_leftovers=True, compute_metrics=True)

    def batch_recompute_lookthrough(self, from_date: date, to_date: date):
        if not self.primary_portfolio or not self.is_lookthrough:
            raise ValueError(
                "Lookthrough position can only be computed on lookthrough portfolio with a primary portfolio"
            )
        positions = []
        for val_date in pd.date_range(from_date, to_date, freq="B").date:
            portfolio_total_asset_value = (
                self.get_total_asset_under_management(val_date) if not self.only_weighting else None
            )
            positions.extend(self.primary_portfolio.get_lookthrough_positions(val_date, portfolio_total_asset_value))
        self.bulk_create_positions(list(positions), delete_leftovers=True, compute_metrics=False)

    def update_preferred_classification_per_instrument(self):
        # Function to automatically assign Preferred instrument based on the assets' underlying instruments of the
        # attached wbportfolio
        instruments = filter(
            None,
            map(
                lambda x: Instrument.objects.get(id=x["underlying_instrument"]).get_classifable_ancestor(
                    include_self=True
                ),
                self.assets.values("underlying_instrument").distinct("underlying_instrument"),
            ),
        )
        leftovers_instruments = list(
            PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(portfolio=self).values_list(
                "instrument", flat=True
            )
        )
        for instrument in instruments:
            other_classifications = instrument.classifications.filter(group__is_primary=False)
            default_classification = None
            if other_classifications.count() == 1:
                default_classification = other_classifications.first()
            if not PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(
                portfolio=self, instrument=instrument
            ).exists():
                PortfolioInstrumentPreferredClassificationThroughModel.objects.create(
                    portfolio=self,
                    instrument=instrument,
                    classification=default_classification,
                    classification_group=default_classification.group if default_classification else None,
                )
            if instrument.id in leftovers_instruments:
                leftovers_instruments.remove(instrument.id)

        for instrument_id in leftovers_instruments:
            PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(
                portfolio=self, instrument=instrument_id
            ).delete()

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:portfolio"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:portfoliorepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    def bulk_create_positions(self, positions: list[AssetPosition], delete_leftovers: bool = False, **kwargs):
        if positions:
            update_dates = set()
            for position in positions:
                position.portfolio = self
                update_dates.add(position.date)
            # self.assets.filter(date__in=update_dates, is_estimated=True).delete()
            leftover_positions_ids = list(
                self.assets.filter(date__in=update_dates).values_list("id", flat=True)
            )  # we need to get the ids otherwise the queryset is reevaluated later
            logger.info(f"bulk saving {len(positions)} positions ({len(leftover_positions_ids)} leftovers) ...")
            objs = AssetPosition.unannotated_objects.bulk_create(
                positions,
                update_fields=[
                    "weighting",
                    "initial_price",
                    "initial_currency_fx_rate",
                    "initial_shares",
                    "currency_fx_rate_instrument_to_usd",
                    "currency_fx_rate_portfolio_to_usd",
                    "underlying_quote_price",
                    "is_estimated",
                    "portfolio",
                    "portfolio_created",
                    "underlying_instrument",
                ],
                unique_fields=["portfolio", "date", "underlying_quote", "portfolio_created"],
                update_conflicts=True,
                batch_size=10000,
            )
            if delete_leftovers:
                objs_ids = list(map(lambda x: x.id, objs))
                leftover_positions_ids = list(filter(lambda i: i not in objs_ids, leftover_positions_ids))
                logger.info(f"deleting {len(leftover_positions_ids)} leftover positions..")
                AssetPosition.objects.filter(id__in=leftover_positions_ids).delete()
            for update_date in sorted(update_dates):
                self.change_at_date(update_date, **kwargs)

    @classmethod
    def _get_or_create_portfolio(cls, instrument_handler, portfolio_data):
        if isinstance(portfolio_data, int):
            return Portfolio.objects.get(id=portfolio_data)
        instrument = portfolio_data
        if isinstance(portfolio_data, dict):
            instrument = instrument_handler.process_object(instrument, only_security=False, read_only=True)[0]
        return instrument.primary_portfolio

    def check_share_diff(self, val_date: date) -> bool:
        return self.assets.filter(Q(date=val_date) & ~Q(initial_shares=F("initial_shares_at_custodian"))).exists()

    def get_returns(
        self,
        from_date: date,
        to_date: date,
        ffill_returns: bool = True,
        convert_to_portfolio_currency: bool = True,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Utility methods to get instrument returns for a given date range

        Args:
            from_date: date range lower bound
            to_date: date range upper bound

        Returns:
            Return a tuple of the returns and the last prices series for conveniance
        """
        instruments = list(
            self.assets.filter(date__gte=from_date, date__lte=to_date)
            .values_list("underlying_quote", flat=True)
            .distinct("underlying_quote")
        )
        prices = InstrumentPrice.objects.filter(
            instrument__in=instruments, date__gte=from_date, date__lte=to_date
        ).annotate(
            fx_rate=CurrencyFXRates.get_fx_rates_subquery_for_two_currencies(
                "date", "instrument__currency", self.currency
            ),
            price_fx_portfolio=F("net_value") * F("fx_rate") if convert_to_portfolio_currency else F("net_value"),
        )
        prices_df = (
            pd.DataFrame(
                prices.filter_only_valid_prices().values_list("instrument", "price_fx_portfolio", "date"),
                columns=["instrument", "price_fx_portfolio", "date"],
            )
            .pivot_table(index="date", values="price_fx_portfolio", columns="instrument")
            .astype(float)
            .sort_index()
        )
        if prices_df.empty:
            raise InvalidAnalyticPortfolio()
        ts = pd.bdate_range(prices_df.index.min(), prices_df.index.max(), freq="B")
        prices_df = prices_df.reindex(ts)
        if ffill_returns:
            prices_df = prices_df.ffill()
        returns = prices_to_returns(prices_df, drop_inceptions_nan=False, fill_nan=ffill_returns)
        return returns.replace([np.inf, -np.inf, np.nan], 0), prices_df.replace([np.inf, -np.inf, np.nan], None)

    @classmethod
    def get_contribution_df(
        cls,
        qs,
        need_normalize=False,
        groupby_label_id="underlying_instrument",
        groubpy_label_title="underlying_instrument__name_repr",
        currency_fx_rate_label="currency_fx_rate",
        hedged_currency=None,
    ):
        # qs = AssetPosition.annotate_underlying_instrument(qs)
        weight_label = "weighting" if not need_normalize else "total_value_fx_portfolio"
        qs = qs.annotate(
            is_hedged=Case(
                When(
                    underlying_instrument__currency__isnull=False,
                    underlying_instrument__currency=hedged_currency,
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
            coalesce_currency_fx_rate=Case(
                When(is_hedged=True, then=Value(Decimal(1.0))),
                default=F(currency_fx_rate_label),
                output_field=models.BooleanField(),
            ),
        ).select_related("underlying_instrument")
        df = pd.DataFrame(
            qs.values_list(
                "date",
                "price",
                "coalesce_currency_fx_rate",
                groupby_label_id,
                groubpy_label_title,
                weight_label,
            ),
            columns=[
                "date",
                "price",
                "coalesce_currency_fx_rate",
                groupby_label_id,
                groubpy_label_title,
                weight_label,
            ],
        )
        if not df.empty:
            df = df[df[weight_label] != 0]
            df.date = pd.to_datetime(df.date)
            df["price_fx_portfolio"] = df.price * df.coalesce_currency_fx_rate

            df[["price", "price_fx_portfolio", weight_label, "coalesce_currency_fx_rate"]] = df[
                ["price", "price_fx_portfolio", weight_label, "coalesce_currency_fx_rate"]
            ].astype("float")

            df[groupby_label_id] = df[groupby_label_id].fillna(0)
            df[groubpy_label_title] = df[groubpy_label_title].fillna("N/A")
            df_static = df[[groupby_label_id, groubpy_label_title]].groupby(groupby_label_id, dropna=False).first()

            df = (
                df[
                    [
                        groupby_label_id,
                        "date",
                        "price",
                        "price_fx_portfolio",
                        weight_label,
                        "coalesce_currency_fx_rate",
                    ]
                ]
                .groupby(["date", groupby_label_id], dropna=False)
                .agg(
                    {
                        "price": "mean",
                        "price_fx_portfolio": "mean",
                        weight_label: "sum",
                        "coalesce_currency_fx_rate": "mean",
                    }
                )
                .reset_index()
                .set_index("date")
                .sort_index()
            )
            df[weight_label] = df[weight_label].fillna(0)
            value = df.pivot_table(
                index="date",
                columns=[groupby_label_id],
                values=weight_label,
                fill_value=0,
                aggfunc="sum",
            )
            weights_ = value
            if need_normalize:
                total_value_price = df[weight_label].groupby("date", dropna=False).sum()
                weights_ = value.divide(total_value_price, axis=0)
            prices_usd = (
                df.pivot_table(
                    index="date",
                    columns=[groupby_label_id],
                    values="price_fx_portfolio",
                    aggfunc="mean",
                )
                .replace(0, np.nan)
                .bfill()
            )

            rates_fx = (
                df.pivot_table(
                    index="date",
                    columns=[groupby_label_id],
                    values="coalesce_currency_fx_rate",
                    aggfunc="mean",
                )
                .replace(0, np.nan)
                .bfill()
            )

            prices_usd = prices_usd.ffill()
            performance_prices = prices_usd / prices_usd.shift(1, axis=0) - 1
            contributions_prices = performance_prices.multiply(weights_.shift(1, axis=0)).dropna(how="all")
            total_contrib_prices = (1 + contributions_prices.sum(axis=1)).shift(1, fill_value=1.0).cumprod()
            contributions_prices = contributions_prices.multiply(total_contrib_prices, axis=0).sum(skipna=False)
            monthly_perf_prices = (1 + performance_prices).dropna(how="all").product(axis=0, skipna=False) - 1

            rates_fx = rates_fx.ffill()
            performance_rates_fx = rates_fx / rates_fx.shift(1, axis=0) - 1
            contributions_rates_fx = performance_rates_fx.multiply(weights_.shift(1, axis=0)).dropna(how="all")
            total_contrib_rates_fx = (1 + contributions_rates_fx.sum(axis=1)).shift(1, fill_value=1.0).cumprod()
            contributions_rates_fx = contributions_rates_fx.multiply(total_contrib_rates_fx, axis=0).sum(skipna=False)
            monthly_perf_rates_fx = (1 + performance_rates_fx).dropna(how="all").product(axis=0, skipna=False) - 1

            res = pd.concat(
                [
                    df_static,
                    monthly_perf_prices,
                    monthly_perf_rates_fx,
                    contributions_prices,
                    contributions_rates_fx,
                    weights_.iloc[0, :],
                    weights_.iloc[-1, :],
                    value.iloc[0, :],
                    value.iloc[-1, :],
                ],
                axis=1,
            ).reset_index()
            res.columns = [
                groupby_label_id,
                groubpy_label_title,
                "performance_total",
                "performance_forex",
                "contribution_total",
                "contribution_forex",
                "allocation_start",
                "allocation_end",
                "total_value_start",
                "total_value_end",
            ]

            return res.replace([np.inf, -np.inf, np.nan], 0)
        return pd.DataFrame()

    def get_or_create_index(self):
        index = Index.objects.create(name=self.name, currency=self.currency)
        index.portfolios.all().delete()
        InstrumentPortfolioThroughModel.objects.update_or_create(instrument=index, defaults={"portfolio": self})

    @classmethod
    def create_model_portfolio(cls, name: str, currency: Currency, with_index: bool = True):
        portfolio = cls.objects.create(
            is_manageable=True,
            name=name,
            currency=currency,
        )
        if with_index:
            portfolio.get_or_create_index()
        return portfolio


def default_estimate_net_value(val_date: date, instrument: Instrument) -> float | None:
    portfolio = instrument.portfolio
    previous_val_date = (val_date - BDay(1)).date()

    if (
        portfolio.assets.filter(date=previous_val_date).exists()
        and (  # we assume that in t-1 we will have a portfolio (with at least estimate position). If we use the latest position date before val_date, we run into the problem of being able to compute nav at every date
            last_price := instrument.get_latest_price(previous_val_date)
        )
    ):
        with suppress(
            IndexError, InvalidAnalyticPortfolio
        ):  # we silent any indexerror introduced by no returns for the past days
            analytic_portfolio, _ = portfolio.get_analytic_portfolio(previous_val_date)
            return analytic_portfolio.get_estimate_net_value(float(last_price.net_value))


@receiver(post_save, sender="wbportfolio.PortfolioPortfolioThroughModel")
def post_portfolio_relationship_creation(sender, instance, created, raw, **kwargs):
    if (
        not raw
        and created
        and instance.portfolio.is_lookthrough
        and instance.type == PortfolioPortfolioThroughModel.Type.PRIMARY
    ):
        with suppress(AssetPosition.DoesNotExist):
            earliest_primary_position_date = instance.dependency_portfolio.assets.earliest("date").date
            batch_recompute_lookthrough_as_task.delay(
                instance.portfolio.id, earliest_primary_position_date, date.today()
            )


@shared_task(queue="portfolio")
def trigger_portfolio_change_as_task(portfolio_id, val_date, **kwargs):
    portfolio = Portfolio.all_objects.get(id=portfolio_id)
    portfolio.change_at_date(val_date, **kwargs)


@shared_task(queue="portfolio")
def batch_recompute_lookthrough_as_task(portfolio_id: int, start: date, end: date):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    portfolio.batch_recompute_lookthrough(start, end)


@receiver(investable_universe_updated, sender="wbfdm.Instrument")
def update_portfolio_after_investable_universe(*args, end_date: date | None = None, **kwargs):
    if not end_date:
        end_date = date.today()
    end_date = (end_date + timedelta(days=1) - BDay(1)).date()  # shift in case of business day
    from_date = (end_date - BDay(1)).date()
    for portfolio in Portfolio.tracked_objects.all().to_dependency_iterator(from_date):
        if not portfolio.is_lookthrough:
            try:
                portfolio.propagate_or_update_assets(from_date, end_date)
            except Exception as e:
                logger.error(f"Exception while propagating portfolio assets {portfolio}: {e}")
        portfolio.estimate_net_asset_values(end_date)
