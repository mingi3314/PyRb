import abc
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


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
        ...


class EbestOrderManager(OrderManager):
    def __init__(self) -> None:
        ...

    def place_order(self, order: Order) -> None:
        ...


def order_manager_factory(brokerage_name: str) -> OrderManager:
    if brokerage_name == "ebest":
        return EbestOrderManager()
    else:
        raise ValueError("Invalid order manager type")
