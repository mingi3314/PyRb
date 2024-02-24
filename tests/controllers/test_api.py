from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from pyrb.controllers.api.deps import account_repo_dep
from pyrb.controllers.api.main import app
from pyrb.repositories.account import AccountRepository

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


def create_account() -> Response:
    request_data = {
        "brokerage": "ebest",
        "app_key": "your_app_key",
        "secret_key": "your_secret_key",
    }

    response = client.post("/accounts", json=request_data)
    return response


def test_create_account() -> None:
    # When
    response = create_account()

    # Then
    assert response.status_code == 201
    assert "account_id" in response.json()


def test_get_default_account_with_created_account() -> None:
    # Given
    response = create_account()
    account_id = response.json()["account_id"]

    # When
    response = client.get("/accounts/default")

    # Then
    assert response.status_code == 200
    assert response.json()["account"]["id"] == account_id


def test_get_default_account_without_created_account() -> None:
    # When
    response = client.get("/accounts/default")

    # Then
    assert response.status_code == 404
    assert response.json() == {"detail": "No accounts registered"}
