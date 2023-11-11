from abc import ABC, abstractmethod
from pathlib import Path

from pyrb.model.account import Account


class AccountRepository(ABC):
    @abstractmethod
    def set(self, account: Account) -> None: ...


class LocalConfigAccountRepository(AccountRepository):
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        # create directory if not exists
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

    def set(self, account: Account) -> None:
        with open(self._config_path, "w") as f:
            f.write(account.to_toml())
