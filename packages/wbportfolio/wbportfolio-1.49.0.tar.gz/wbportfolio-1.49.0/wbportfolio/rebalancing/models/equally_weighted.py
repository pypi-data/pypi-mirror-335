from decimal import Decimal

from wbportfolio.pms.typing import Portfolio
from wbportfolio.rebalancing.base import AbstractRebalancingModel
from wbportfolio.rebalancing.decorators import register


@register("Equally Weighted Rebalancing")
class EquallyWeightedRebalancing(AbstractRebalancingModel):
    def is_valid(self) -> bool:
        return self.portfolio.assets.filter(date=self.last_effective_date).exists()

    def get_target_portfolio(self) -> Portfolio:
        positions = []
        assets = self.portfolio.assets.filter(date=self.last_effective_date)
        nb_assets = assets.count()
        for asset in assets:
            asset.date = self.trade_date
            asset.asset_valuation_date = self.trade_date
            positions.append(asset._build_dto(new_weight=Decimal(1 / nb_assets)))
        return Portfolio(positions=tuple(positions))
