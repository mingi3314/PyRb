from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def create_target_weights(self) -> dict[str, float]:
        """
        Returns a dictionary with asset symbols as keys and target allocation percentages as values.
        """
        ...
