from pyrb.model.account import Account, EbestAccount
from pyrb.repository.brokerage.base.client import BrokerageAPIClient
from pyrb.repository.brokerage.base.fetcher import PriceFetcher
from pyrb.repository.brokerage.base.order_manager import OrderManager
from pyrb.repository.brokerage.base.portfolio import Portfolio
from pyrb.repository.brokerage.ebest.client import EbestAPIClient
from pyrb.repository.brokerage.ebest.fetcher import EbestPriceFetcher
from pyrb.repository.brokerage.ebest.order_manager import EbestOrderManager
from pyrb.repository.brokerage.ebest.portfolio import EbestPortfolio


class BrokerageAPIClientFactory:
    def __init__(self) -> None: ...

    def create(self, account: Account) -> BrokerageAPIClient:
        match account:
            case EbestAccount():
                return EbestAPIClient(account)
            case _:
                raise NotImplementedError(f"Unsupported account: {account}")


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
