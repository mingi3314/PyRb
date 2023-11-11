from abc import ABC
from typing import Annotated

from pydantic import BaseModel, Field


class Account(BaseModel, ABC): ...


class EbestAccount(Account):
    app_key: Annotated[str, Field(...)]
    app_secret: Annotated[str, Field(...)]
