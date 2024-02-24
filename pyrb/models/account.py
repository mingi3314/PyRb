import uuid
from abc import ABC
from typing import Annotated, Any

import toml
from pydantic import BaseModel, Field

from pyrb.enums import BrokerageType


class Account(BaseModel, ABC):
    brokerage: Annotated[BrokerageType, Field(...)]
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    def to_toml(self) -> str:
        model_dict = self.model_dump()
        model_dict.update({"brokerage": self.brokerage.value})
        return toml.dumps(model_dict)


class EbestAccount(Account):
    app_key: Annotated[str, Field(...)]
    app_secret: Annotated[str, Field(...)]


class AccountFactory:
    @staticmethod
    def create(brokerage: BrokerageType, **kwargs: Any) -> Account:
        if brokerage == BrokerageType.EBEST.value:
            return EbestAccount(brokerage=brokerage, **kwargs)
        raise ValueError(f"brokerage {brokerage} is not supported")
