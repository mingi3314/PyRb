from pyrb.model.account import Account
from pyrb.repository.account import AccountRepository


class AccountService:
    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    def set(self, account: Account) -> None:
        self._account_repo.set(account)

    def get(self) -> Account:
        return self._account_repo.get()
