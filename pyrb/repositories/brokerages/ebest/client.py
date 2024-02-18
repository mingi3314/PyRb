from typing import Any

import requests
from requests import Response

from pyrb.models.account import EbestAccount
from pyrb.repositories.brokerages.base.client import BrokerageAPIClient


class EbestAPIClient(BrokerageAPIClient):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"

    def __init__(self, account: EbestAccount) -> None:
        self._account = account

        self._access_token = self._issue_access_token()

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

        self._raise_for_status(response)

        return response

    def _issue_access_token(self) -> str:
        path = "oauth2/token"
        url = f"{self.BASE_URL}/{path}"

        app_key = self._account.app_key
        app_secret = self._account.app_secret

        headers = {"content-type": "application/x-www-form-urlencoded"}
        params = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "appsecretkey": app_secret,
            "scope": "oob",
        }

        response = requests.post(url, headers=headers, params=params)

        self._raise_for_status(response)

        return response.json()["access_token"]

    def _raise_for_status(self, response: Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            # error_code = response.json()["rsp_cd"]
            # error_msg = response.json()["rsp_msg"]
            status_code = response.status_code
            print(response)
            raise Exception(f"API client error: {status_code}, {response}") from e
