import pytest
from pytest_mock import MockerFixture

from pyrb.enums import BrokerageType
from pyrb.exceptions import InitializationError
from pyrb.models.account import Account, AccountFactory
from pyrb.services.account import AccountService


def test_sut_get_account_with_local_config_account_repository(
    mocker: MockerFixture, account_service: AccountService
) -> None:
    # given
    class FakeAccount(Account):
        foo: str

    fake_account = FakeAccount(foo="bar", brokerage=BrokerageType.EBEST)
    mocker.patch.object(
        AccountFactory,
        "create",
        return_value=fake_account,
    )

    account_service.set(fake_account)

    # when
    account = account_service.get()

    # then
    assert account == fake_account


def test_sut_could_not_get_account_before_set_account(account_service: AccountService) -> None:
    # then
    with pytest.raises(InitializationError):
        # when
        account_service.get()
