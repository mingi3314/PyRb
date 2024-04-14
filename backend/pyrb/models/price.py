from pydantic import BaseModel


class CurrentPrice(BaseModel):
    symbol: str
    price: int
