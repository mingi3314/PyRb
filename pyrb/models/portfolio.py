from pydantic import AwareDatetime, BaseModel


class PortfolioReturn(BaseModel):
    dt: AwareDatetime
    rtn: float
    pnl: float
