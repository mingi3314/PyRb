import abc

from pydantic import BaseModel

from pyrb.repositories.client import BrokerageAPIClient, EbestAPIClient


class CurrentPrice(BaseModel):
    symbol: str
    price: int
    # TODO: 우선매도잔량, 우선매수잔량 추가


class PriceFetcher(abc.ABC):
    def __init__(self) -> None:
        ...

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


def price_fetcher_factory(brokerage_api_client: BrokerageAPIClient) -> PriceFetcher:
    if isinstance(brokerage_api_client, EbestAPIClient):
        return EbestPriceFetcher(brokerage_api_client)
    else:
        raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")
