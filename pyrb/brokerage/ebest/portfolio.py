from pydantic import PositiveFloat
from requests import Response

from pyrb.brokerage.base.portfolio import Portfolio, Position
from pyrb.brokerage.ebest.client import EbestAPIClient


class EbestPortfolio(Portfolio):
    def __init__(self, api_client: EbestAPIClient) -> None:
        self._api_client = api_client

    @property
    def total_value(self) -> PositiveFloat:
        response = self._fetch_portfolio()
        res = response.json()

        return res["t0424OutBlock"]["sunamt"]

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
