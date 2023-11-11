from pathlib import Path
from typing import Annotated

import typer

from pyrb.model.account import EbestAccount
from pyrb.repository.account import LocalConfigAccountRepository
from pyrb.service.account import AccountService

app = typer.Typer()
APP_NAME = "pyrb"  # TODO: parse from pyproject.toml and move to constants.py


@app.command("set")
def set(
    app_key: Annotated[str, typer.Option(..., help="app key for the brokerage", prompt=True)],
    app_secret: Annotated[str, typer.Option(..., help="app secret for the brokerage", prompt=True)],
) -> None:
    app_config_dir = Path(typer.get_app_dir(APP_NAME))
    accounts_config_path = app_config_dir / "accounts"

    account_service = AccountService(
        account_repo=LocalConfigAccountRepository(accounts_config_path)
    )

    account_service.set(account=EbestAccount(app_key=app_key, app_secret=app_secret))
