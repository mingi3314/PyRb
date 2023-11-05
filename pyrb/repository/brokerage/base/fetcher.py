import abc

from pydantic import BaseModel


class CurrentPrice(BaseModel):
    symbol: str
    price: int
    # TODO: 우선매도잔량, 우선매수잔량 추가


class PriceFetcher(abc.ABC):
    def __init__(self) -> None: ...

    @abc.abstractmethod
    def get_current_price(self, symbol: str) -> CurrentPrice:
        """특정 종목의 현재가를 조회합니다.

        Args:
            symbol: 종목코드

        Returns:
            CurrentPrice 객체
        """
        ...

    @abc.abstractmethod
    def get_current_prices(self, symbols: list[str]) -> dict[str, CurrentPrice]:
        """복수 종목의 현재가를 조회합니다.

        Args:
            symbols: 종목코드 리스트

        Returns:
            키는 종목코드, 값은 CurrentPrice 객체로 매핑된 딕셔너리
        """
        ...
