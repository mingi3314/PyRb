from abc import ABC, abstractmethod
from pathlib import Path

import toml

from pyrb.model.account import Account, EbestAccount


class AccountRepository(ABC):
    @abstractmethod
    def set(self, account: Account) -> None: ...

    @abstractmethod
    def get(self) -> Account: ...


class LocalConfigAccountRepository(AccountRepository):
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        # create directory if not exists
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

    def set(self, account: Account) -> None:
        with open(self._config_path, "w") as f:
            f.write(account.to_toml())

    def get(self) -> Account:
        with open(self._config_path) as f:
            return EbestAccount(**toml.loads(f.read()))
