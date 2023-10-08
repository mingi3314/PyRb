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
