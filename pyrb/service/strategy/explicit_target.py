import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path

import yaml

from pyrb.exceptions import InvalidTargetError
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


def read_targets_from_source(source: Path) -> dict[str, float]:
    """
    Reads the target weights from the specified source.
    currently surpports sources are:
    - csv file
    - json file
    - yaml file

    Args:
        source (Path): The source to read the target weights from.

    Returns:
        dict[str, float]: A dictionary mapping asset symbols to target weights.

    """
    match source.suffix:
        case ".csv":
            return CSVTargetReader().read(source)
        case ".json":
            return JSONTargetReader().read(source)
        case ".yaml":
            return YAMLTargetReader().read(source)
        case _:
            raise InvalidTargetError(f"Unsupported source file type: {source.suffix}")


class TargetReader(ABC):
    """
    Abstract class representing a reader for target allocations.
    Provides functionality to read, validate, and normalize target allocations.

    """

    def read(self, source: Path) -> dict[str, float]:
        """
        Reads, validates, and normalizes target allocations from the given source.

        Args:
            source (Path): The source to read the target allocations from.

        Returns:
            dict[str, float]: A dictionary mapping asset symbols to target weights.

        Raises:
            InvalidTargetError: If the target allocations are invalid.
        """
        targets = self._read_targets(source)
        self._validate_targets(targets)
        normalized_targets = self._normalize_targets(targets)
        return normalized_targets

    def _validate_targets(self, targets: dict[str, float]) -> None:
        def _validate_symbol(symbol: str) -> None:
            if not isinstance(symbol, str):
                raise InvalidTargetError("Target symbol must be a string")

        def _validate_weight(weight: float) -> None:
            if not isinstance(weight, float):
                raise InvalidTargetError("Target weight must be a float")

            if weight <= 0:
                raise InvalidTargetError("Target weight must be positive")

        if not isinstance(targets, dict):
            raise InvalidTargetError("Targets must be a dictionary")

        for symbol, weight in targets.items():
            _validate_symbol(symbol)
            _validate_weight(weight)

    def _normalize_targets(self, targets: dict[str, float]) -> dict[str, float]:
        total_weight = sum(targets.values())
        normalized_targets = {symbol: weight / total_weight for symbol, weight in targets.items()}
        return normalized_targets

    @abstractmethod
    def _read_targets(self, source: Path) -> dict[str, float]:
        """
        Read the targets from the given source.

        Args:
            source (Path): The source to read the target weights from.

        Returns:
            dict[str, float]: A dictionary mapping asset symbols to target weights.
        """
        ...


class CSVTargetReader(TargetReader):
    def _read_targets(self, source: Path) -> dict[str, float]:
        with open(source, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            targets = {row["symbol"]: float(row["weight"]) for row in reader}
            return targets


class JSONTargetReader(TargetReader):
    def _read_targets(self, source: Path) -> dict[str, float]:
        with open(source) as jsonfile:
            targets = json.load(jsonfile)
            return targets


class YAMLTargetReader(TargetReader):
    def _read_targets(self, source: Path) -> dict[str, float]:
        with open(source) as yamlfile:
            targets = yaml.safe_load(yamlfile)
            return targets
