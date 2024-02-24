import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pyrb.controllers.cli.main import app
from pyrb.enums import OrderSide, OrderType
from pyrb.exceptions import InsufficientFundsException
from pyrb.models.order import Order
from pyrb.repositories.brokerages.context import RebalanceContext
from pyrb.services.rebalance import Rebalancer


def test_sut_rebalances(fake_rebalance_context: RebalanceContext, mocker: MockerFixture) -> None:
    """Test rebalance command with fake rebalance context"""

    # given
    runner = CliRunner()

    mocker.patch(
        "pyrb.controllers.cli.main.create_rebalance_context", return_value=fake_rebalance_context
    )

    spy = mocker.spy(fake_rebalance_context.order_manager, "place_order")

    # when
    result = runner.invoke(app, ["holding-portfolio", "--investment-amount", "1000"], input="y\n")

    # then
    assert result.exit_code == 0
    assert spy.call_count == 2
    assert spy.call_args_list == [
        mocker.call(
            Order(
                symbol="000660",
                price=100,
                quantity=95,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
            ),
        ),
        mocker.call(
            Order(
                symbol="005930",
                price=150,
                quantity=47,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
            ),
        ),
    ]


def test_sut_rebalances_with_only_buy_orders(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch(
        "pyrb.controllers.cli.main.create_rebalance_context", return_value=fake_rebalance_context
    )

    # when
    result = runner.invoke(app, ["holding-portfolio", "--investment-amount", "20000"])

    # then
    assert "BUY" in result.output
    assert "SELL" not in result.output


def test_sut_rebalances_with_only_sell_order(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch(
        "pyrb.controllers.cli.main.create_rebalance_context", return_value=fake_rebalance_context
    )

    # when
    result = runner.invoke(app, ["holding-portfolio", "--investment-amount", "1000"])

    # then
    assert "SELL" in result.output
    assert "BUY" not in result.output


def test_sut_stops_rebalancing_with_disallowance_from_user(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch(
        "pyrb.controllers.cli.main.create_rebalance_context", return_value=fake_rebalance_context
    )

    # when
    result = runner.invoke(app, ["holding-portfolio", "--investment-amount", "1000"], input="n\n")

    # then
    assert result.exit_code == 0
    assert "No orders were placed" in result.output


def test_sut_stops_rebalancing_with_insufficient_funds(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch(
        "pyrb.controllers.cli.main.create_rebalance_context", return_value=fake_rebalance_context
    )

    # when
    result = runner.invoke(
        app, ["holding-portfolio", "--investment-amount", "999999999"], input="y\n"
    )

    # then
    assert result.exit_code == 1
    assert result.exc_info[0] == InsufficientFundsException


@pytest.mark.parametrize(
    "targets_source",
    [
        "tests/resources/fake_targets.csv",
        "tests/resources/fake_targets.json",
        "tests/resources/fake_targets.yaml",
    ],
)
def test_sut_rebalance_with_explicit_target_from_json_source(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture, targets_source: str
) -> None:
    """
    Check if rebalancing with explicit targets from a JSON source works as expected.
    The portfolio used as a test double has following positions:
    - 100 shares of 000660 @ 100 (total amount: 10000)
    - 50 shares of 005930 @ 150 (total amount: 7500)

    The target weights and current prices are:
    - 40% of 005930 (current price: 150)
    - 30% of 000660 (current price: 100)
    - 30% of 035420 (current price: 100)

    The total investment amount is 10000.
    The expected orders are:
    - Sell 24 shares of 005930 to leave 26 shares (value: 3900)
    - Sell 70 shares of 000660 to leave 30 shares (value: 3000)
    - Buy 30 shares of 035420 (value: 3000)

    The expected total amount of the portfolio after rebalancing is 9900.
    """
    # given
    runner = CliRunner()

    mocker.patch(
        "pyrb.controllers.cli.main.create_rebalance_context", return_value=fake_rebalance_context
    )

    spy = mocker.spy(Rebalancer, "place_orders")

    # when
    result = runner.invoke(
        app,
        [
            "explicit-target",
            "--targets-source",
            targets_source,
            "--investment-amount",
            "10000",
        ],
        input="y\n",
    )

    # then
    assert result.exit_code == 0
    assert spy.call_count == 1

    _, args = spy.call_args[0]
    assert args == [
        Order(
            symbol="005930",
            price=150,
            quantity=24,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
        ),
        Order(
            symbol="000660",
            price=100,
            quantity=70,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
        ),
        Order(
            symbol="035420",
            price=100,
            quantity=30,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
        ),
    ]
