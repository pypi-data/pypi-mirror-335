from wbportfolio.pms.typing import Portfolio
from wbportfolio.rebalancing.base import AbstractRebalancingModel
from wbportfolio.rebalancing.decorators import register


@register("Model Portfolio Rebalancing")
class ModelPortfolioRebalancing(AbstractRebalancingModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def model_portfolio_rel(self):
        return self.portfolio.dependency_through.filter(type="MODEL").first()

    @property
    def model_portfolio(self):
        if model_portfolio_rel := self.model_portfolio_rel:
            return model_portfolio_rel.dependency_portfolio

    def is_valid(self) -> bool:
        return (
            self.model_portfolio.assets.filter(date=self.last_effective_date).exists()
            if self.model_portfolio
            else False
        )

    def get_target_portfolio(self) -> Portfolio:
        positions = []
        assets = self.model_portfolio.get_positions(self.last_effective_date)

        for asset in assets:
            asset.date = self.trade_date
            asset.asset_valuation_date = self.trade_date
            positions.append(asset._build_dto())
        return Portfolio(positions=tuple(positions))
