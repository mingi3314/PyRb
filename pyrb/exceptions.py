class PyRbException(Exception):
    pass


class InsufficientFundsException(PyRbException):
    pass


class PaperTradingSettingError(PyRbException):
    pass


class OrderPlacementError(PyRbException):
    pass


class InvalidTargetError(PyRbException):
    pass


class APIClientError(PyRbException):
    def __init__(self, client_error_code: str, client_error_message: str, status_code: int) -> None:
        self.client_error_code = client_error_code
        self.client_error_message = client_error_message
        self.status_code = status_code
