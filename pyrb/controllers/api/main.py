from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pyrb.controllers.api.deps import AccountServiceDep
from pyrb.exceptions import InitializationError
from pyrb.models.account import Account

app = FastAPI()


class AccountResponse(BaseModel):
    account: Account


@app.get("/accounts/default", response_model=AccountResponse)
async def get_default_account(account_service: AccountServiceDep) -> AccountResponse:
    try:
        account = account_service.get()
    except InitializationError as e:
        raise HTTPException(status_code=404, detail="No accounts registered") from e

    return AccountResponse(account=account)
