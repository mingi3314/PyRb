class PyRbException(Exception): ...


class InsufficientFundsException(PyRbException): ...


class PaperTradingSettingError(PyRbException): ...


class OrderPlacementError(PyRbException): ...


class InvalidTargetError(PyRbException): ...


class InitializationError(PyRbException): ...


class APIClientError(PyRbException):
    def __init__(self, client_error_code: str, client_error_message: str, status_code: int) -> None:
        self.client_error_code = client_error_code
        self.client_error_message = client_error_message
        self.status_code = status_code
