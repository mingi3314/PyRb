import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AwareDatetime, BaseModel
from starlette.status import HTTP_201_CREATED

from pyrb.controllers.api.deps import AccountServiceDep, RebalanceContextDep
from pyrb.enums import AssetAllocationStrategyEnum, BrokerageType
from pyrb.exceptions import InitializationError
from pyrb.models.account import Account, AccountFactory
from pyrb.models.order import OrderPlacementResult
from pyrb.services.rebalance import Rebalancer
from pyrb.services.strategy.asset_allocate import AssetAllocationStrategyFactory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:1420",  # tauri
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AccountResponse(BaseModel):
    account: Account


class AccountCreateRequest(BaseModel):
    brokerage: BrokerageType
    app_key: str
    secret_key: str


class AccountCreateResponse(BaseModel):
    account_id: UUID


class RebalanceRequest(BaseModel):
    investment_amount: float | None


class RebalanceResponse(BaseModel):
    rebalanced_at: AwareDatetime
    placed_orders: list[OrderPlacementResult]


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


# TODO: Swagger에서 StrEnum이 제대로 표시되지 않는 문제 원인 파악 후 수정
@app.post("/strategies/{strategy_type}/rebalance", response_model=RebalanceResponse)
async def rebalance(
    context: RebalanceContextDep, strategy_type: AssetAllocationStrategyEnum, body: RebalanceRequest
) -> RebalanceResponse:
    strategy = AssetAllocationStrategyFactory.create(strategy_type)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=body.investment_amount)
    placed_orders = rebalancer.place_orders(orders)

    return RebalanceResponse(
        rebalanced_at=datetime.datetime.now(ZoneInfo("Asia/Seoul")),
        placed_orders=placed_orders,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
