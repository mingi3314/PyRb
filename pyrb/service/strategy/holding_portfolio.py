from pyrb.brokerage.context import RebalanceContext
from pyrb.service.strategy.base import Strategy


class HoldingPortfolioRebalanceStrategy(Strategy):
    """
    A rebalancing strategy
    that creates target weights for a portfolio based on the current holdings.

    Args:
        portfolio (Portfolio): The portfolio to rebalance.
    """

    def __init__(self, context: RebalanceContext) -> None:
        self._context = context

    def create_target_weights(self) -> dict[str, float]:
        holding_symbols = self._context._portfolio.holding_symbols
        return {stock: 1 / len(holding_symbols) for stock in holding_symbols}
