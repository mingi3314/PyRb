from pydantic import BaseModel, PositiveFloat, PositiveInt, computed_field

from pyrb.enums import AssetClassEnum

asset_class_by_symbols: dict[str, AssetClassEnum] = {
    "361580": AssetClassEnum.STOCK,  # KBSTAR 200TR
    "379800": AssetClassEnum.STOCK,  # KODEX 미국S&P500TR
    "411060": AssetClassEnum.COMMODITY,  # ACE KRX금현물
    "365780": AssetClassEnum.BOND,  # ACE 국고채10년
    "308620": AssetClassEnum.BOND,  # KODEX 미국채10년선물
    "272580": AssetClassEnum.CASH,  # TIGER 단기채권액티브
    "005930": AssetClassEnum.STOCK,  # 삼성전자
    "000660": AssetClassEnum.STOCK,  # SK하이닉스
}


class Asset(BaseModel):
    symbol: str  # 종목코드
    label: str  # 종목명

    @computed_field
    def asset_class(self) -> str:
        return asset_class_by_symbols.get(self.symbol, AssetClassEnum.OTHER)


class Position(BaseModel):
    asset: Asset  # 종목코드
    quantity: PositiveInt  # 보유수량
    sellable_quantity: PositiveInt  # 매도가능수량
    average_buy_price: PositiveFloat  # 매입단가
    total_amount: PositiveFloat  # 평가금액
    rtn: float  # 수익률
    profit: float  # 수익금
