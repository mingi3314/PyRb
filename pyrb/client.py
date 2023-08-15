from typing import Any

import requests
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import Response


class EbestConfig(BaseSettings):
    # secret
    APP_KEY: str
    APP_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="EBEST_")


class EbestAPIClient:
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    config = EbestConfig()

    def __init__(self) -> None:
        self._access_token = self._issue_access_token()

    def fetch_current_prices(self, symbols: list[str]) -> Response:
        path = "stock/market-data"
        content_type = "application/json; charset=UTF-8"

        headers = {"content-type": content_type, "tr_cd": "t8407", "tr_cont": "N"}
        body = {
            "t8407InBlock": {
                "nrec": len(symbols),  # 조회할 종목 수
                "shcode": "".join(symbols),  # 종목코드
            }
        }

        response = self._make_request("POST", path, headers=headers, json=body)
        return response

    def get_portfolio(self) -> Response:
        path = "stock/accno"
        content_type = "application/json; charset=UTF-8"

        headers = {"content-type": content_type, "tr_cd": "t0424", "tr_cont": "N"}
        body = {
            "t0424InBlock": {
                "prcgb": "",
                "chegb": "",
                "dangb": "",
                "charge": "",
                "cts_expcode": "",
            }
        }

        response = self._make_request("POST", path, headers=headers, json=body)
        return response

    def _make_request(self, method: str, path: str, **kwargs: Any) -> Response:
        URL = f"{self.BASE_URL}/{path}"
        headers = kwargs.get("headers", {})
        headers["authorization"] = f"Bearer {self._access_token}"
        kwargs["headers"] = headers

        response = requests.request(method, URL, **kwargs)

        # If token expired, renew and retry once
        if response.status_code == 401:  # Assuming 401 status code indicates an expired token
            self._access_token = self._issue_access_token()
            headers["authorization"] = f"Bearer {self._access_token}"
            response = requests.request(method, URL, **kwargs)

        response.raise_for_status()
        return response

    def _issue_access_token(self) -> str:
        path = "oauth2/token"
        url = f"{self.BASE_URL}/{path}"

        headers = {"content-type": "application/x-www-form-urlencoded"}
        params = {
            "grant_type": "client_credentials",
            "appkey": self.config.APP_KEY,
            "appsecretkey": self.config.APP_SECRET,
            "scope": "oob",
        }

        response = requests.post(url, verify=False, headers=headers, params=params)
        response.raise_for_status()
        return response.json()["access_token"]
