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
    def total_value(self) -> PositiveFloat:
        """Calculates the total value of the portfolio.
        total value = cash + sum of the market value of all positions

        Returns:
            PositiveFloat: The total value of the portfolio.
        """
        ...

    @property
    @abc.abstractmethod
    def positions(self) -> list[Position]:
        """Returns a list of all positions in the portfolio.

        Returns:
            list[Position]: A list of all positions in the portfolio.
        """
        ...

    @property
    @abc.abstractmethod
    def holding_symbols(self) -> list[str]:
        """Returns a list of symbols for all positions in the portfolio.

        Returns:
            list[str]: A list of symbols for all positions in the portfolio.
        """
        ...

    @abc.abstractmethod
    def get_position(self, symbol: str) -> Position | None:
        """Returns the position object for the given symbol.

        Args:
            symbol : The symbol of the position to retrieve.

        Returns:
            Position | None: The position object for the given symbol,
                             if the symbol is not found, None will be returned.
        """
        ...
