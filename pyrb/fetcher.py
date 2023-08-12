import abc

from pydantic import BaseModel


class CurrentPrice(BaseModel):
    symbol: str
    price: int
    # TODO: 우선매도잔량, 우선매수잔량 추가


class PriceFetcher(abc.ABC):
    def __init__(self) -> None:
        ...

    @abc.abstractmethod
    def get_current_price(self, symbol: str) -> CurrentPrice:
        ...

    @abc.abstractmethod
    def get_current_prices(self, symbols: list[str]) -> dict[str, CurrentPrice]:
        ...


class EbestPriceFetcher(PriceFetcher):
    def __init__(self) -> None:
        ...

    def get_current_price(self, symbol: str) -> CurrentPrice:
        ...

    def get_current_prices(self, symbols: list[str]) -> dict[str, CurrentPrice]:
        ...


def price_fetcher_factory(brokerage_name: str) -> PriceFetcher:
    if brokerage_name == "ebest":
        return EbestPriceFetcher()
    else:
        raise ValueError("Invalid price fetcher type")
