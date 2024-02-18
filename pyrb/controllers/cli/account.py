from typing import Annotated

import typer

from pyrb.controllers.constants import APP_DIR
from pyrb.enums import BrokerageType
from pyrb.models.account import AccountFactory
from pyrb.repositories.account import LocalConfigAccountRepository
from pyrb.services.account import AccountService

app = typer.Typer()


@app.command("set")
def set(
    app_key: Annotated[str, typer.Option(..., help="app key for the brokerage", prompt=True)],
    app_secret: Annotated[str, typer.Option(..., help="app secret for the brokerage", prompt=True)],
    brokerage: Annotated[
        BrokerageType, typer.Option(help="brokerage type", case_sensitive=False)
    ] = BrokerageType.EBEST,
) -> None:
    account_service = create_account_service()
    account = AccountFactory.create(brokerage, app_key=app_key, app_secret=app_secret)
    account_service.set(account=account)


def create_account_service() -> AccountService:
    app_dir = APP_DIR
    accounts_config_path = app_dir / "accounts"

    account_service = AccountService(
        account_repo=LocalConfigAccountRepository(accounts_config_path)
    )

    return account_service
