from pydantic import BaseModel

from pyrb.enums import OrderSide, OrderType


class Order(BaseModel):
    symbol: str  # 종목코드
    price: int  # 주문가격
    quantity: int  # 주문수량
    side: OrderSide  # 매매구분
    order_type: OrderType  # 주문유형

    def __str__(self) -> str:
        return f"{self.symbol}: {self.side} {self.quantity} shares @ {self.price}"


class OrderPlacementResult(BaseModel):
    order: Order
    success: bool
    message: str | None = None
