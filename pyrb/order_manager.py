import abc

from pyrb.client import BrokerageAPIClient, EbestAPIClient
from pyrb.order import Order


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
