from abc import ABC
from typing import Annotated

import toml
from pydantic import BaseModel, Field


class Account(BaseModel, ABC):
    def to_toml(self) -> str:
        return toml.dumps(self.model_dump())


class EbestAccount(Account):
    app_key: Annotated[str, Field(...)]
    app_secret: Annotated[str, Field(...)]
