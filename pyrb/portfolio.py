import abc

from pydantic import BaseModel, PositiveFloat, PositiveInt


class Position(BaseModel):
    symbol: str  # 종목코드
    quantity: PositiveInt  # 보유수량
    sellable_quantity: PositiveInt  # 매도가능수량
    average_buy_price: PositiveFloat  # 매입단가
    total_amount: PositiveFloat  # 평가금액


class Portfolio(abc.ABC):
    def __init__(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def positions(self) -> list[Position]:
        ...

    @property
    @abc.abstractmethod
    def holding_symbols(self) -> list[str]:
        ...


class EbestPortfolio(Portfolio):
    def __init__(self) -> None:
        ...

    @property
    def positions(self) -> list[Position]:
        ...

    @property
    def holding_symbols(self) -> list[str]:
        return [position.symbol for position in self.positions]


def portfolio_factory(brokerage_name: str) -> Portfolio:
    if brokerage_name == "ebest":
        return EbestPortfolio()
    else:
        raise ValueError("Invalid portfolio type")
