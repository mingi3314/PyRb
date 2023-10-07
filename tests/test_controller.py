from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pyrb.brokerage.base.order_manager import Order, OrderSide, OrderStatus, OrderType
from pyrb.brokerage.context import RebalanceContext
from pyrb.controller import app
from pyrb.exceptions import InsufficientFundsException
from pyrb.service.rebalance import Rebalancer


def test_sut_rebalances(fake_rebalance_context: RebalanceContext, mocker: MockerFixture) -> None:
    """Test rebalance command with fake rebalance context"""

    # given
    runner = CliRunner()

    mocker.patch("pyrb.controller.create_rebalance_context", return_value=fake_rebalance_context)

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
                status=OrderStatus.PLACED,
            ),
        ),
        mocker.call(
            Order(
                symbol="005930",
                price=150,
                quantity=46,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                status=OrderStatus.PLACED,
            ),
        ),
    ]


def test_sut_rebalances_with_only_buy_orders(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch("pyrb.controller.create_rebalance_context", return_value=fake_rebalance_context)

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

    mocker.patch("pyrb.controller.create_rebalance_context", return_value=fake_rebalance_context)

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

    mocker.patch("pyrb.controller.create_rebalance_context", return_value=fake_rebalance_context)

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

    mocker.patch("pyrb.controller.create_rebalance_context", return_value=fake_rebalance_context)

    # when
    result = runner.invoke(
        app, ["holding-portfolio", "--investment-amount", "999999999"], input="y\n"
    )

    # then
    assert result.exit_code == 1
    assert result.exc_info[0] == InsufficientFundsException


def test_sut_rebalance_with_explicit_target_from_json_source(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    """
    Check if rebalancing with explicit targets from a JSON source works as expected.
    The portfolio used as a test double has following positions:
    - 100 shares of 000660 @ 100 (total amount: 10000)
    - 50 shares of 005930 @ 150 (total amount: 7500)

    The target weights are:
    - 40% of 005930
    - 30% of 000660
    - 30% of 035420

    The total investment amount is 1000.
    The expected orders are:
    - Sell 71 shares of 005930
    - Sell 97 shares of 000660
    - Buy 3 shares of 035420

    The expected total amount of the portfolio after rebalancing is 1000.


    """
    # given
    runner = CliRunner()

    mocker.patch("pyrb.controller.create_rebalance_context", return_value=fake_rebalance_context)

    spy = mocker.spy(Rebalancer, "place_orders")

    # when
    result = runner.invoke(
        app,
        [
            "explicit-target",
            "--targets-source",
            "tests/resources/fake_targets.json",
            "--investment-amount",
            "1000",
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
            price=100,
            quantity=71,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            status=OrderStatus.PLACED,
        ),
        Order(
            symbol="000660",
            price=100,
            quantity=97,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            status=OrderStatus.PLACED,
        ),
        Order(
            symbol="035420",
            price=100,
            quantity=3,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            status=OrderStatus.PLACED,
        ),
    ]
