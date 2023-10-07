from abc import abstractmethod

from pyrb.brokerage.base.portfolio import Portfolio
from pyrb.service.strategy.base import Strategy


class DirectRebalancingStrategy(Strategy):
    @abstractmethod
    def create_target_weights(self) -> dict[str, float]: ...


class HoldingPortfolioRebalancingStrategy(Strategy):
    def __init__(self, portfolio: Portfolio) -> None:
        self._portfolio = portfolio

    def create_target_weights(self) -> dict[str, float]:
        holding_symbols = self._portfolio.holding_symbols
        return {stock: 1 / len(holding_symbols) for stock in holding_symbols}
