import abc
from typing import Any

from requests import Response


class BrokerageAPIClient(abc.ABC):
    @abc.abstractmethod
    def send_request(self, method: str, path: str, **kwargs: Any) -> Response: ...
