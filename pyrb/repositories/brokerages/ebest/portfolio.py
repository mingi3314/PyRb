from typing import Any

from pydantic import NonNegativeFloat

from pyrb.models.position import Asset, Position
from pyrb.repositories.brokerages.base.portfolio import Portfolio
from pyrb.repositories.brokerages.ebest.client import EbestAPIClient


class EbestPortfolio(Portfolio):
    def __init__(self, api_client: EbestAPIClient) -> None:
        self._api_client = api_client
        self._serialized_portfolio: dict[str, Any] = self._fetch_portfolio()

    @property
    def total_value(self) -> NonNegativeFloat:
        return self._serialized_portfolio["t0424OutBlock"]["sunamt"]

    @property
    def cash_balance(self) -> NonNegativeFloat:
        return self._serialized_portfolio["CSPAQ12200OutBlock2"]["D2Dps"]

    @property
    def positions(self) -> list[Position]:
        positions = [
            Position(
                asset=Asset(symbol=item["expcode"], label=item["hname"]),
                quantity=item["janqty"],
                sellable_quantity=item["mdposqt"],
                average_buy_price=item["pamt"],
                total_amount=item["appamt"],
                rtn=float(item["sunikrt"]) / 100,
            )
            for item in self._serialized_portfolio["t0424OutBlock1"]
        ]

        return positions

    @property
    def holding_symbols(self) -> list[str]:
        return [position.asset.symbol for position in self.positions]

    def get_position(self, symbol: str) -> Position | None:
        return next(
            (position for position in self.positions if position.asset.symbol == symbol), None
        )

    def get_position_amount(self, symbol: str) -> NonNegativeFloat:
        position = self.get_position(symbol)
        return position.total_amount if position else 0

    def refresh(self) -> None:
        self._serialized_portfolio = self._fetch_portfolio()

    def _fetch_portfolio(self) -> dict[str, Any]:
        asset_balance = self._fetch_assets_balance()
        cash_balance = self._fetch_cash_balance()
        return asset_balance | cash_balance

    def _fetch_assets_balance(self) -> dict[str, Any]:
        """주식잔고2 TR(t0424)을 조회합니다.
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
        return response.json()

    def _fetch_cash_balance(self) -> dict[str, Any]:
        """현물계좌예수금 주문가능금액 총평가 조회 TR(CSPAQ12200)을 조회합니다.
        see: https://openapi.ebestsec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=37d22d4d-83cd-40a4-a375-81b010a4a627
        """
        path = "stock/accno"
        content_type = "application/json; charset=UTF-8"

        headers = {"content-type": content_type, "tr_cd": "CSPAQ12200", "tr_cont": "N"}

        body = {
            "CSPAQ12200InBlock1": {
                "BalCreTp": "0",
            }
        }

        response = self._api_client.send_request("POST", path, headers=headers, json=body)
        return response.json()
