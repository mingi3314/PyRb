from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from pyrb.controllers.api.deps import account_repo_dep, context_dep
from pyrb.controllers.api.main import AccountCreateResponse, app
from pyrb.repositories.account import AccountRepository
from pyrb.repositories.brokerages.context import RebalanceContext

client = TestClient(app)


@pytest.fixture(autouse=True)
def use_tmp_path_for_account_repo(
    tmp_account_repo: AccountRepository,
) -> Generator[None, None, None]:
    """
    테스트 과정에서 실제 운영 환경의 파일을 수정하지 않도록 임시 디렉토리를 사용합니다.
    account_repo_dep 의존성을 임시 디렉토리를 사용하는 AccountRepository 로 오버라이드합니다.
    매 테스트 실행 전에 임시 디렉토리를 사용하도록 설정하고, 테스트 종료 후에는 설정을 초기화합니다.
    """
    app.dependency_overrides[account_repo_dep] = lambda: tmp_account_repo
    yield
    app.dependency_overrides.clear()


def create_account() -> AccountCreateResponse:
    request_data = {
        "brokerage": "ebest",
        "app_key": "your_app_key",
        "secret_key": "your_secret_key",
    }

    response = client.post("/accounts", json=request_data)
    return AccountCreateResponse.model_validate(response.json())


def test_create_account() -> None:
    # When
    response = create_account()

    # Then
    assert "account_id" in response.model_dump(mode="json")


def test_get_default_account_with_created_account() -> None:
    # Given
    response = create_account()
    account_id = response.account_id

    # When
    response = client.get("/accounts/default")

    # Then
    assert response.status_code == 200
    assert response.json()["account"]["id"] == str(account_id)


def test_get_default_account_without_created_account() -> None:
    # When
    response = client.get("/accounts/default")

    # Then
    assert response.status_code == 404
    assert response.json() == {"detail": "No accounts registered"}


def test_prepare_orders(fake_rebalance_context: RebalanceContext) -> None:
    # Given
    create_account()
    app.dependency_overrides[context_dep] = lambda: fake_rebalance_context

    # When
    response = client.get(
        "/strategies/all-weather-kr/orders",
    )

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "orders": [
            {
                "symbol": "379800",
                "price": 100,
                "quantity": 173,
                "side": "BUY",
                "order_type": "MARKET",
            },
            {
                "symbol": "361580",
                "price": 100,
                "quantity": 173,
                "side": "BUY",
                "order_type": "MARKET",
            },
            {
                "symbol": "411060",
                "price": 100,
                "quantity": 148,
                "side": "BUY",
                "order_type": "MARKET",
            },
            {
                "symbol": "365780",
                "price": 100,
                "quantity": 173,
                "side": "BUY",
                "order_type": "MARKET",
            },
            {
                "symbol": "308620",
                "price": 100,
                "quantity": 173,
                "side": "BUY",
                "order_type": "MARKET",
            },
            {
                "symbol": "272580",
                "price": 100,
                "quantity": 148,
                "side": "BUY",
                "order_type": "MARKET",
            },
        ]
    }
    app.dependency_overrides.clear()


@freeze_time("2024-01-03T00:00:00+09:00")
def test_place_orders(fake_rebalance_context: RebalanceContext) -> None:
    # Given
    create_account()
    app.dependency_overrides[context_dep] = lambda: fake_rebalance_context
    orders = client.get("/strategies/all-weather-kr/orders").json()["orders"]

    # When
    response = client.post(
        "/strategies/all-weather-kr/orders",
        json={"orders": orders},
    )

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "placed_at": "2024-01-03T00:00:00+09:00",
        "placed_orders": [
            {
                "order": {
                    "symbol": "379800",
                    "price": 100,
                    "quantity": 173,
                    "side": "BUY",
                    "order_type": "MARKET",
                },
                "success": True,
                "message": None,
            },
            {
                "order": {
                    "symbol": "361580",
                    "price": 100,
                    "quantity": 173,
                    "side": "BUY",
                    "order_type": "MARKET",
                },
                "success": True,
                "message": None,
            },
            {
                "order": {
                    "symbol": "411060",
                    "price": 100,
                    "quantity": 148,
                    "side": "BUY",
                    "order_type": "MARKET",
                },
                "success": True,
                "message": None,
            },
            {
                "order": {
                    "symbol": "365780",
                    "price": 100,
                    "quantity": 173,
                    "side": "BUY",
                    "order_type": "MARKET",
                },
                "success": True,
                "message": None,
            },
            {
                "order": {
                    "symbol": "308620",
                    "price": 100,
                    "quantity": 173,
                    "side": "BUY",
                    "order_type": "MARKET",
                },
                "success": True,
                "message": None,
            },
            {
                "order": {
                    "symbol": "272580",
                    "price": 100,
                    "quantity": 148,
                    "side": "BUY",
                    "order_type": "MARKET",
                },
                "success": True,
                "message": None,
            },
        ],
    }
    app.dependency_overrides.clear()


def test_get_portfolio(fake_rebalance_context: RebalanceContext) -> None:
    # Given
    create_account()
    app.dependency_overrides[context_dep] = lambda: fake_rebalance_context

    # When
    response = client.get("/portfolio")

    # Then
    assert response.status_code == 200

    actual = response.json()
    expected = {
        "total_value": 100000,
        "cash_balance": 0,
        "positions": [
            {
                "asset": {"symbol": "000660", "label": "SK하이닉스", "asset_class": "STOCK"},
                "quantity": 100,
                "sellable_quantity": 100,
                "average_buy_price": 100,
                "total_amount": 10000,
                "rtn": 0.0,
            },
            {
                "asset": {"symbol": "005930", "label": "삼성전자", "asset_class": "STOCK"},
                "quantity": 50,
                "sellable_quantity": 50,
                "average_buy_price": 150,
                "total_amount": 7500,
                "rtn": 0.0,
            },
        ],
    }

    assert actual == expected

    app.dependency_overrides.clear()


def test_get_portfolio_without_account() -> None:
    # When
    response = client.get("/portfolio")

    # Then
    assert response.status_code == 404
    assert response.json() == {"detail": "account is not set. Please set account first"}
