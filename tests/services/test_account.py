import tempfile
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pyrb.enums import BrokerageType
from pyrb.exceptions import InitializationError
from pyrb.model.account import Account, AccountFactory
from pyrb.repository.account import LocalConfigAccountRepository
from pyrb.service.account import AccountService


def test_sut_set_account_with_local_config_account_repository(mocker: MockerFixture) -> None:
    # given
    class FakeAccount(Account):
        foo: str

    fake_account = FakeAccount(foo="bar", brokerage=BrokerageType.EBEST)
    mocker.patch.object(
        AccountFactory,
        "create",
        return_value=fake_account,
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        config_path = Path(tmpdirname) / "accounts"
        account_repo = LocalConfigAccountRepository(config_path)
        account_service = AccountService(account_repo)

        # when
        account_service.set(fake_account)

        # then
        with open(config_path) as f:
            assert f.read() == fake_account.to_toml()


def test_sut_get_account_with_local_config_account_repository(mocker: MockerFixture) -> None:
    # given
    class FakeAccount(Account):
        foo: str

    fake_account = FakeAccount(foo="bar", brokerage=BrokerageType.EBEST)
    mocker.patch.object(
        AccountFactory,
        "create",
        return_value=fake_account,
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        config_path = Path(tmpdirname) / "accounts"
        account_repo = LocalConfigAccountRepository(config_path)
        account_service = AccountService(account_repo)

        account_service.set(fake_account)

        # when
        account = account_service.get()

        # then
        assert account == fake_account


def test_sut_could_not_get_account_before_set_account(mocker: MockerFixture) -> None:
    # given
    with tempfile.TemporaryDirectory() as tmpdirname:
        config_path = Path(tmpdirname) / "accounts"
        account_repo = LocalConfigAccountRepository(config_path)
        account_service = AccountService(account_repo)

        # then
        with pytest.raises(InitializationError):
            # when
            account_service.get()
