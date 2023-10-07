from abc import abstractmethod

from pyrb.service.strategy.base import Strategy


class AssetAllocationStrategy(Strategy):
    @abstractmethod
    def create_target_weights(self) -> dict[str, float]: ...


class AllWeatherKRStrategy(AssetAllocationStrategy):
    def __init__(self) -> None: ...

    def create_target_weights(self) -> dict[str, float]:
        return {
            "379800": 0.175,  # (주식) KODEX 미국S&P500TR
            "361580": 0.175,  # (주식) KBSTAR 200TR
            "411060": 0.15,  # (금) ACE KRX금현물
            "365780": 0.175,  # (국채) ACE 국고채10년
            "308620": 0.175,  # (국채) KODEX 미국채10년선물
            "272580": 0.15,  # (현금성 자산) TIGER 단기채권액티브
        }
