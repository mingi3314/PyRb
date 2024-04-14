from pathlib import Path

import typer

APP_NAME = "pyrb"  # TODO: parse from pyproject.toml and move to constants.py
APP_DIR = Path(typer.get_app_dir(APP_NAME))
ACCOUNTS_CONFIG_PATH = APP_DIR / "accounts"
