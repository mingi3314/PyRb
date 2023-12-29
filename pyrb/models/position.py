from pydantic import BaseModel, PositiveFloat, PositiveInt


class Position(BaseModel):
    symbol: str  # 종목코드
    quantity: PositiveInt  # 보유수량
    sellable_quantity: PositiveInt  # 매도가능수량
    average_buy_price: PositiveFloat  # 매입단가
    total_amount: PositiveFloat  # 평가금액
    rtn: float  # 수익률
