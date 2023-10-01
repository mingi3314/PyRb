import abc
from enum import StrEnum

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


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    PLACED = "PLACED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Order(BaseModel):
    symbol: str  # 종목코드
    price: int  # 주문가격
    quantity: int  # 주문수량
    side: OrderSide  # 매매구분
    order_type: OrderType  # 주문유형
    status: OrderStatus = OrderStatus.PENDING  # 주문상태

    def __str__(self) -> str:
        return f"{self.symbol}: {self.side} {self.quantity} shares @ {self.price}"


class OrderManager(abc.ABC):
    def __init__(self) -> None:
        ...

    @abc.abstractmethod
    def place_order(self, order: Order) -> None:
        """
        Places an order with the brokerage. This method should be implemented by the
        concrete class.
        If the order fails to place, an OrderPlacementError should be raised.

        Args:
            order (Order): The order to place.

        Returns:
            None

        Raises:
            OrderPlacementError: If the order fails to place.
        """
        ...
