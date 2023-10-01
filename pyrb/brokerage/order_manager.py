import abc
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from pyrb.brokerage.client import BrokerageAPIClient, EbestAPIClient


class OrderType(StrEnum):
    LIMIT = "LIMIT"  # 지정가
    MARKET = "MARKET"  # 시장가
    CONDITIONAL_LIMIT = "CONDITIONAL_LIMIT"  # 조건부지정가
    BEST_LIMIT = "BEST_LIMIT"  # 최유리지정가
    IMMEDIATE_LIMIT = "IMMEDIATE_LIMIT"  # 최우선지정가
    PREOPENING_SESSION_LAST = "PREOPENING_SESSION_LAST"  # 장개시전시간외종가
    AFTER_HOURS_LAST = "AFTER_HOURS_LAST"  # 시간외종가
    AFTER_HOURS_SINGLE = "AFTER_HOURS_SINGLE"  # 시간외단일가


class Order(BaseModel):
    symbol: str  # 종목코드
    price: int  # 주문가격
    quantity: int  # 주문수량
    side: Literal["BUY", "SELL"]  # 매매구분
    order_type: OrderType  # 주문유형


class OrderManager(abc.ABC):
    def __init__(self) -> None:
        ...

    @abc.abstractmethod
    def place_order(self, order: Order) -> None:
        """주문을 제출합니다.

        Args:
            order: 주문 객체
        """
        ...


class EbestOrderManager(OrderManager):
    def __init__(self, api_client: EbestAPIClient) -> None:
        self._api_client = api_client

    def place_order(self, order: Order) -> None:
        path = "stock/order"
        content_type = "application/json; charset=UTF-8"

        headers = {"content-type": content_type, "tr_cd": "CSPAT00601", "tr_cont": "N"}
        body = {
            "CSPAT00601InBlock1": {
                "IsuNo": order.symbol,
                "OrdQty": order.quantity,
                "OrdPrc": order.price,
                "BnsTpCode": "2",
                "OrdprcPtnCode": "00",
                "PrgmOrdprcPtnCode": "00",
                "StslAbleYn": "0",
                "StslOrdprcTpCode": "0",
                "CommdaCode": "41",
                "MgntrnCode": "000",
                "LoanDt": "",
                "MbrNo": "000",
                "OrdCndiTpCode": "0",
                "StrtgCode": " ",
                "GrpId": " ",
                "OrdSeqNo": 0,
                "PtflNo": 0,
                "BskNo": 0,
                "TrchNo": 0,
                "ItemNo": 0,
                "OpDrtnNo": "0",
                "LpYn": "0",
                "CvrgTpCode": "0",
            }
        }

        self._api_client.send_request("POST", path, headers=headers, json=body)


def order_manager_factory(brokerage_api_client: BrokerageAPIClient) -> OrderManager:
    if isinstance(brokerage_api_client, EbestAPIClient):
        return EbestOrderManager(brokerage_api_client)
    else:
        raise NotImplementedError(f"Unsupported BrokerageAPIClient: {brokerage_api_client}")
