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
    def total_asset(self) -> PositiveFloat:
        """포트폴리오의 총 자산을 조회합니다."""
        ...

    @property
    @abc.abstractmethod
    def positions(self) -> list[Position]:
        """보유중인 포지션 목록을 조회합니다.

        Returns:
            보유중인 포지션 목록
        """
        ...

    @property
    @abc.abstractmethod
    def holding_symbols(self) -> list[str]:
        """보유중인 종목코드를 조회합니다.

        Returns:
            보유중인 종목코드 리스트
        """
        ...

    @abc.abstractmethod
    def get_position(self, symbol: str) -> Position | None:
        """포지션 정보를 조회합니다.

        Args:
            symbol: 종목코드

        Returns:
            포지션 정보. 종목코드에 해당하는 포지션이 없으면 None을 반환합니다.
        """
        ...
