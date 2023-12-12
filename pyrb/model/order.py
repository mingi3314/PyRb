from pydantic import BaseModel

from pyrb.enums import OrderSide, OrderStatus, OrderType


class Order(BaseModel):
    symbol: str  # 종목코드
    price: int  # 주문가격
    quantity: int  # 주문수량
    side: OrderSide  # 매매구분
    order_type: OrderType  # 주문유형
    status: OrderStatus = OrderStatus.PENDING  # 주문상태

    def __str__(self) -> str:
        return f"{self.symbol}: {self.side} {self.quantity} shares @ {self.price}"
