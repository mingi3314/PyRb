import pytest

from pyrb.fetcher import CurrentPrice, PriceFetcher
from pyrb.main import RebalanceContext
from pyrb.order import Order
from pyrb.order_manager import OrderManager
from pyrb.portfolio import Portfolio, Position


class FakePortfolio(Portfolio):
    def __init__(self) -> None:
        ...

    @property
    def total_asset(self) -> float:
        return 100000

    @property
    def positions(self) -> list[Position]:
        return [
            Position(
                symbol="000660",
                quantity=100,
                sellable_quantity=100,
                average_buy_price=100,
                total_amount=10000,
            ),
            Position(
                symbol="005930",
                quantity=50,
                sellable_quantity=50,
                average_buy_price=150,
                total_amount=7500,
            ),
        ]

    @property
    def holding_symbols(self) -> list[str]:
        return [position.symbol for position in self.positions]

    def get_position(self, symbol: str) -> Position | None:
        return next((position for position in self.positions if position.symbol == symbol), None)


class FakePriceFetcher(PriceFetcher):
    def __init__(self) -> None:
        ...

    def get_current_price(self, symbol: str) -> CurrentPrice:
        return CurrentPrice(symbol=symbol, price=100)

    def get_current_prices(self, symbols: list[str]) -> dict[str, CurrentPrice]:
        return {symbol: CurrentPrice(symbol=symbol, price=100) for symbol in symbols}


class FakeOrderManager(OrderManager):
    def __init__(self) -> None:
        ...

    def place_order(self, order: Order) -> None:
        ...


@pytest.fixture
def fake_rebalance_context() -> RebalanceContext:
    return RebalanceContext(
        portfolio=FakePortfolio(),
        price_fetcher=FakePriceFetcher(),
        order_manager=FakeOrderManager(),
    )
