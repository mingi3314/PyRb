from enum import StrEnum

from pyrb.brokerage.base.client import BrokerageAPIClient, TradeMode
from pyrb.brokerage.base.fetcher import PriceFetcher
from pyrb.brokerage.base.order_manager import OrderManager
from pyrb.brokerage.base.portfolio import Portfolio
from pyrb.brokerage.ebest.client import EbestAPIClient
from pyrb.brokerage.ebest.fetcher import EbestPriceFetcher
from pyrb.brokerage.ebest.order_manager import EbestOrderManager
from pyrb.brokerage.ebest.portfolio import EbestPortfolio


class BrokerageType(StrEnum):
    EBEST = "ebest"


class BrokerageAPIClientFactory:
    def __init__(self) -> None: ...

    def create(self, brokerage: BrokerageType, trade_mode: TradeMode) -> BrokerageAPIClient:
        match brokerage:
            case BrokerageType.EBEST:
                return EbestAPIClient(trade_mode=trade_mode)
            case _:
                raise NotImplementedError(f"Unsupported brokerage: {brokerage}")


class PortfolioFactory:
    def __init__(self) -> None: ...

    def create(self, brokerage_api_client: BrokerageAPIClient) -> Portfolio:
        match brokerage_api_client:
            case EbestAPIClient():
                return EbestPortfolio(brokerage_api_client)
            case _:
                raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")


class PriceFetcherFactory:
    def __init__(self) -> None: ...

    def create(self, brokerage_api_client: BrokerageAPIClient) -> PriceFetcher:
        match brokerage_api_client:
            case EbestAPIClient():
                return EbestPriceFetcher(brokerage_api_client)
            case _:
                raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")


class OrderManagerFactory:
    def __init__(self) -> None: ...

    def create(self, brokerage_api_client: BrokerageAPIClient) -> OrderManager:
        match brokerage_api_client:
            case EbestAPIClient():
                return EbestOrderManager(brokerage_api_client)
            case _:
                raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")
