import tempfile
from pathlib import Path

from pyrb.model.account import Account
from pyrb.repository.account import LocalConfigAccountRepository
from pyrb.service.account import AccountService


def test_sut_set_account_with_local_config_account_repository() -> None:
    # given
    with tempfile.TemporaryDirectory() as tmpdirname:
        config_path = Path(tmpdirname) / "accounts"
        account_repo = LocalConfigAccountRepository(config_path)
        account_service = AccountService(account_repo)

        class FakeAccount(Account):
            foo: str

        # when
        account = FakeAccount(foo="bar")
        account_service.set(account)

        # then
        with open(config_path) as f:
            assert f.read() == account.to_toml()
