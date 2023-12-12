from enum import StrEnum


class BrokerageType(StrEnum):
    EBEST = "ebest"


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


class AssetAllocationStrategyEnum(StrEnum):
    ALL_WEATHER_KR = "all-weather-kr"
