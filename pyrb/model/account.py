from abc import ABC, abstractmethod
from typing import Annotated

import toml
from pydantic import BaseModel, Field

from pyrb.enums import BrokerageType


class Account(BaseModel, ABC):
    @property
    @abstractmethod
    def brokerage(self) -> BrokerageType: ...

    def to_toml(self) -> str:
        return toml.dumps(self.model_dump())


class EbestAccount(Account):
    app_key: Annotated[str, Field(...)]
    app_secret: Annotated[str, Field(...)]

    @property
    def brokerage(self) -> BrokerageType:
        return BrokerageType.EBEST
