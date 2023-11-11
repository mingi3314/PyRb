from pyrb.repository.brokerage.base.client import TradeMode
from pyrb.repository.brokerage.base.fetcher import PriceFetcher
from pyrb.repository.brokerage.base.order_manager import OrderManager
from pyrb.repository.brokerage.base.portfolio import Portfolio
from pyrb.repository.brokerage.factory import (
    BrokerageAPIClientFactory,
    BrokerageType,
    OrderManagerFactory,
    PortfolioFactory,
    PriceFetcherFactory,
)


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


def create_rebalance_context(brokerage: BrokerageType, trade_mode: TradeMode) -> RebalanceContext:
    brokerage_api_client = BrokerageAPIClientFactory().create(brokerage, trade_mode)

    portfolio = PortfolioFactory().create(brokerage_api_client)
    price_fetcher = PriceFetcherFactory().create(brokerage_api_client)
    order_manager = OrderManagerFactory().create(brokerage_api_client)

    rebalance_context = RebalanceContext(portfolio, price_fetcher, order_manager)
    return rebalance_context
