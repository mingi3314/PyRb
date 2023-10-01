from pyrb.brokerage.base.client import BrokerageAPIClient, TradeMode
from pyrb.brokerage.base.fetcher import PriceFetcher
from pyrb.brokerage.base.order_manager import OrderManager
from pyrb.brokerage.base.portfolio import Portfolio
from pyrb.brokerage.ebest.client import EbestAPIClient
from pyrb.brokerage.ebest.fetcher import EbestPriceFetcher
from pyrb.brokerage.ebest.order_manager import EbestOrderManager
from pyrb.brokerage.ebest.portfolio import EbestPortfolio


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


def brokerage_api_client_factory(brokerage_name: str, trade_mode: TradeMode) -> BrokerageAPIClient:
    if brokerage_name == "ebest":
        return EbestAPIClient(trade_mode=trade_mode)
    else:
        raise NotImplementedError(f"Unsupported brokerage: {brokerage_name}")


def price_fetcher_factory(brokerage_api_client: BrokerageAPIClient) -> PriceFetcher:
    if isinstance(brokerage_api_client, EbestAPIClient):
        return EbestPriceFetcher(brokerage_api_client)
    else:
        raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")


def order_manager_factory(brokerage_api_client: BrokerageAPIClient) -> OrderManager:
    if isinstance(brokerage_api_client, EbestAPIClient):
        return EbestOrderManager(brokerage_api_client)
    else:
        raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")


def portfolio_factory(brokerage_api_client: BrokerageAPIClient) -> Portfolio:
    if isinstance(brokerage_api_client, EbestAPIClient):
        return EbestPortfolio(brokerage_api_client)
    else:
        raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")


def create_rebalance_context(brokerage_name: str, trade_mode: TradeMode) -> RebalanceContext:
    brokerage_api_client = brokerage_api_client_factory(brokerage_name, trade_mode)

    portfolio = portfolio_factory(brokerage_api_client)
    price_fetcher = price_fetcher_factory(brokerage_api_client)
    order_manager = order_manager_factory(brokerage_api_client)

    rebalance_context = RebalanceContext(portfolio, price_fetcher, order_manager)
    return rebalance_context
