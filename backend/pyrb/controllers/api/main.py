import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AwareDatetime, BaseModel
from starlette.status import HTTP_201_CREATED

from pyrb.controllers.api.deps import AccountServiceDep, RebalanceContextDep
from pyrb.enums import AssetAllocationStrategyEnum, BrokerageType
from pyrb.exceptions import InitializationError
from pyrb.models.account import Account, AccountFactory
from pyrb.models.order import Order, OrderPlacementResult
from pyrb.models.portfolio import PortfolioReturn
from pyrb.models.position import Position
from pyrb.services.rebalance import Rebalancer
from pyrb.services.strategy.asset_allocate import AssetAllocationStrategyFactory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def ping() -> str:
    return "pong"


class AccountResponse(BaseModel):
    account: Account


class AccountCreateRequest(BaseModel):
    brokerage: BrokerageType
    app_key: str
    secret_key: str


class AccountCreateResponse(BaseModel):
    account_id: UUID


class PortfolioResponse(BaseModel):
    total_value: float
    cash_balance: float
    positions: list[Position]


class PortfolioReturnsResponse(BaseModel):
    start_dt: AwareDatetime
    end_dt: AwareDatetime
    returns: list[PortfolioReturn]


class OrdersPrepareResponse(BaseModel):
    orders: list[Order]


class OrdersPlaceRequest(BaseModel):
    orders: list[Order]


class OrdersPlaceResponse(BaseModel):
    placed_at: AwareDatetime
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


@app.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(context: RebalanceContextDep) -> PortfolioResponse:
    portfolio = context.portfolio

    return PortfolioResponse(
        total_value=portfolio.total_value,
        cash_balance=portfolio.cash_balance,
        positions=portfolio.positions,
    )


@app.get("/portfolio/returns", response_model=PortfolioReturnsResponse)
async def fetch_portfolio_returns(
    context: RebalanceContextDep,
    start_dt: AwareDatetime = Query(),
    end_dt: AwareDatetime = Query(
        default_factory=lambda: datetime.datetime.now(ZoneInfo("Asia/Seoul"))
    ),
) -> PortfolioReturnsResponse:
    returns = context.portfolio.fetch_returns(start_dt, end_dt)

    return PortfolioReturnsResponse(
        start_dt=start_dt,
        end_dt=end_dt,
        returns=returns,
    )


@app.get("/strategies/{strategy_type}/orders", response_model=OrdersPrepareResponse)
async def prepare_orders(
    context: RebalanceContextDep,
    strategy_type: AssetAllocationStrategyEnum,
) -> OrdersPrepareResponse:
    strategy = AssetAllocationStrategyFactory.create(strategy_type)
    rebalancer = Rebalancer(context)

    orders = rebalancer.prepare_orders(
        strategy=strategy, investment_amount=context.portfolio.total_value * 0.99
    )

    return OrdersPrepareResponse(
        orders=orders,
    )


@app.post("/strategies/{strategy_type}/orders", response_model=OrdersPlaceResponse)
async def place_orders(
    context: RebalanceContextDep,
    body: OrdersPlaceRequest,
) -> OrdersPlaceResponse:
    rebalancer = Rebalancer(context)
    placed_orders = rebalancer.place_orders(body.orders)
    return OrdersPlaceResponse(
        placed_at=datetime.datetime.now(ZoneInfo("Asia/Seoul")),
        placed_orders=placed_orders,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
