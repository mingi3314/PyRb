import abc

from pydantic import BaseModel, PositiveFloat, PositiveInt
from requests import Response

from pyrb.client import BrokerageAPIClient, EbestAPIClient


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


class EbestPortfolio(Portfolio):
    def __init__(self, api_client: EbestAPIClient) -> None:
        self._api_client = api_client

    @property
    def positions(self) -> list[Position]:
        response = self._fetch_portfolio()
        res = response.json()

        positions = [
            Position(
                symbol=item["expcode"],
                quantity=item["janqty"],
                sellable_quantity=item["mdposqt"],
                average_buy_price=item["pamt"],
                total_amount=item["appamt"],
            )
            for item in res["t0424OutBlock1"]
        ]

        return positions

    @property
    def holding_symbols(self) -> list[str]:
        return [position.symbol for position in self.positions]

    def get_position(self, symbol: str) -> Position | None:
        return next((position for position in self.positions if position.symbol == symbol), None)

    def _fetch_portfolio(self) -> Response:
        """주식잔고2 TR을 조회합니다.

        see: https://openapi.ebestsec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=37d22d4d-83cd-40a4-a375-81b010a4a627
        """
        path = "stock/accno"
        content_type = "application/json; charset=UTF-8"

        headers = {"content-type": content_type, "tr_cd": "t0424", "tr_cont": "N"}
        body = {
            "t0424InBlock": {
                "prcgb": "",
                "chegb": "",
                "dangb": "",
                "charge": "",
                "cts_expcode": "",
            }
        }

        response = self._api_client.send_request("POST", path, headers=headers, json=body)
        return response


def portfolio_factory(brokerage_api_client: BrokerageAPIClient) -> Portfolio:
    if isinstance(brokerage_api_client, EbestAPIClient):
        return EbestPortfolio(brokerage_api_client)
    else:
        raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")
