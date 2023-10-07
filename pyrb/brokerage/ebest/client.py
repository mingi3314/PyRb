from typing import Any

import requests
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import Response

from pyrb.brokerage.base.client import BrokerageAPIClient, TradeMode


class EbestClientConfig(BaseSettings):
    # secret
    APP_KEY: str
    APP_SECRET: str

    PAPER_APP_KEY: str | None = None
    PAPER_APP_SECRET: str | None = None

    model_config = SettingsConfigDict(env_prefix="EBEST_")


class EbestAPIClient(BrokerageAPIClient):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"

    def __init__(self, trade_mode: TradeMode = TradeMode.PAPER) -> None:
        self._trade_mode = trade_mode
        self._access_token = self._issue_access_token()
        self._config = EbestClientConfig()

    def send_request(self, method: str, path: str, **kwargs: Any) -> Response:
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

        match self._trade_mode:
            case TradeMode.REAL:
                app_key = self._config.APP_KEY
                app_secret = self._config.APP_SECRET
            case TradeMode.PAPER:
                app_key = self._config.PAPER_APP_KEY
                app_secret = self._config.PAPER_APP_SECRET

        headers = {"content-type": "application/x-www-form-urlencoded"}
        params = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "appsecretkey": app_secret,
            "scope": "oob",
        }

        response = requests.post(url, verify=False, headers=headers, params=params)
        response.raise_for_status()
        return response.json()["access_token"]
