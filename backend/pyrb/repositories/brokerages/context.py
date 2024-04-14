from pyrb.models.account import Account
from pyrb.repositories.brokerages.base.fetcher import PriceFetcher
from pyrb.repositories.brokerages.base.order_manager import OrderManager
from pyrb.repositories.brokerages.base.portfolio import Portfolio
from pyrb.repositories.brokerages.factory import (
    BrokerageAPIClientFactory,
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


def create_rebalance_context(account: Account) -> RebalanceContext:
    brokerage_api_client = BrokerageAPIClientFactory().create(account)

    portfolio = PortfolioFactory().create(brokerage_api_client)
    price_fetcher = PriceFetcherFactory().create(brokerage_api_client)
    order_manager = OrderManagerFactory().create(brokerage_api_client)

    rebalance_context = RebalanceContext(portfolio, price_fetcher, order_manager)
    return rebalance_context
