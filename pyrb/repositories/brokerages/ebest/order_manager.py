from requests import HTTPError

from pyrb.enums import OrderType
from pyrb.exceptions import OrderPlacementError
from pyrb.models.order import Order
from pyrb.repositories.brokerages.base.order_manager import OrderManager
from pyrb.repositories.brokerages.ebest.client import EbestAPIClient


class EbestOrderManager(OrderManager):
    _order_type_mapping: dict[OrderType, str] = {
        OrderType.LIMIT: "00",
        OrderType.MARKET: "03",
        OrderType.CONDITIONAL_LIMIT: "05",
        OrderType.BEST_LIMIT: "06",
        OrderType.IMMEDIATE_LIMIT: "07",
        OrderType.PREOPENING_SESSION_LAST: "61",
        OrderType.AFTER_HOURS_LAST: "81",
        OrderType.AFTER_HOURS_SINGLE: "82",
    }

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
                "BnsTpCode": "2" if order.side == "BUY" else "1",
                "OrdprcPtnCode": self._order_type_mapping[order.order_type],
                "MgntrnCode": "000",
                "LoanDt": "",
                "OrdCndiTpCode": "0",
            }
        }

        try:
            resp = self._api_client.send_request("POST", path, headers=headers, json=body).json()
            if resp.get("rsp_cd") != "00040":
                raise OrderPlacementError(resp)
        except HTTPError as e:
            raise OrderPlacementError(e)
