from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED

from pyrb.controllers.api.deps import AccountServiceDep
from pyrb.enums import BrokerageType
from pyrb.exceptions import InitializationError
from pyrb.models.account import Account, AccountFactory

app = FastAPI()


class AccountResponse(BaseModel):
    account: Account


class AccountCreateRequest(BaseModel):
    brokerage: BrokerageType
    app_key: str
    secret_key: str


class AccountCreateResponse(BaseModel):
    account_id: UUID


@app.get("/accounts/default", response_model=AccountResponse)
async def get_default_account(account_service: AccountServiceDep) -> AccountResponse:
    try:
        account = account_service.get()
    except InitializationError as e:
        raise HTTPException(status_code=404, detail="No accounts registered") from e

    return AccountResponse(account=account)


@app.post("/accounts", response_model=AccountCreateResponse, status_code=HTTP_201_CREATED)
async def create_account(
    account_service: AccountServiceDep, body: AccountCreateRequest
) -> AccountCreateResponse:
    account = AccountFactory.create(
        brokerage=body.brokerage, app_key=body.app_key, app_secret=body.secret_key
    )
    account_service.set(account)

    return AccountCreateResponse(account_id=account.id)
