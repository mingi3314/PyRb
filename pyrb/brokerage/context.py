from pyrb.brokerage.client import TradeMode, brokerage_api_client_factory
from pyrb.brokerage.fetcher import PriceFetcher, price_fetcher_factory
from pyrb.brokerage.order_manager import OrderManager, order_manager_factory
from pyrb.brokerage.portfolio import Portfolio, portfolio_factory


class RebalanceContext:
    def __init__(
        self, portfolio: Portfolio, price_fetcher: PriceFetcher, order_manager: OrderManager
    ) -> None:
        self._portfolio = portfolio
        self._price_fetcher = price_fetcher
        self._order_manager = order_manager

    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio

    @property
    def price_fetcher(self) -> PriceFetcher:
        return self._price_fetcher

    @property
    def order_manager(self) -> OrderManager:
        return self._order_manager


def create_rebalance_context(brokerage_name: str, trade_mode: TradeMode) -> RebalanceContext:
    brokerage_api_client = brokerage_api_client_factory(brokerage_name, trade_mode)

    portfolio = portfolio_factory(brokerage_api_client)
    price_fetcher = price_fetcher_factory(brokerage_api_client)
    order_manager = order_manager_factory(brokerage_api_client)

    rebalance_context = RebalanceContext(portfolio, price_fetcher, order_manager)
    return rebalance_context
