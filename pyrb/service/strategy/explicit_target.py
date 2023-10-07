from pyrb.service.strategy.base import Strategy


class ExplicitTargetRebalanceStrategy(Strategy):
    """
    A rebalancing strategy that uses explicit target weights for each asset.

    Args:
        targets (dict[str, float]): A dictionary mapping asset symbols to target weights.

    """

    def __init__(self, targets: dict[str, float]) -> None:
        self._targets = targets

    def create_target_weights(self) -> dict[str, float]:
        return self._targets
