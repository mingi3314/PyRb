from pyrb.repository.brokerage.base.fetcher import CurrentPrice, PriceFetcher
from pyrb.repository.brokerage.ebest.client import EbestAPIClient


class EbestPriceFetcher(PriceFetcher):
    def __init__(self, api_client: EbestAPIClient) -> None:
        self._api_client = api_client

    def get_current_price(self, symbol: str) -> CurrentPrice:
        return self.get_current_prices([symbol])[symbol]

    def get_current_prices(self, symbols: list[str]) -> dict[str, CurrentPrice]:
        path = "stock/market-data"
        content_type = "application/json; charset=UTF-8"

        headers = {"content-type": content_type, "tr_cd": "t8407", "tr_cont": "N"}
        body = {
            "t8407InBlock": {
                "nrec": len(symbols),  # 조회할 종목 수
                "shcode": "".join(symbols),  # 종목코드
            }
        }

        response = self._api_client.send_request("POST", path, headers=headers, json=body)

        res = response.json()
        current_prices = {
            item["shcode"]: CurrentPrice(symbol=item["shcode"], price=item["price"])
            for item in res["t8407OutBlock1"]
        }
        return current_prices
