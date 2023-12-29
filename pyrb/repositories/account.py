from abc import ABC, abstractmethod
from pathlib import Path

import toml

from pyrb.exceptions import InitializationError
from pyrb.models.account import Account, AccountFactory


class AccountRepository(ABC):
    @abstractmethod
    def set(self, account: Account) -> None: ...

    @abstractmethod
    def get(self) -> Account: ...


class LocalConfigAccountRepository(AccountRepository):
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        # create config file within a directory if not exists
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.touch(exist_ok=True)

    def set(self, account: Account) -> None:
        with open(self._config_path, "w") as f:
            f.write(account.to_toml())

    def get(self) -> Account:
        with open(self._config_path) as f:
            account_config = toml.loads(f.read())
            if not account_config:
                raise InitializationError("account is not set. Please set account first")

            brokerage = account_config.pop("brokerage")
            account = AccountFactory.create(brokerage=brokerage, **account_config)

            return account
