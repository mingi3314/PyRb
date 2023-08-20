from click.testing import CliRunner
from pytest_mock import MockerFixture

from pyrb.main import RebalanceContext, cli
from pyrb.order import Order, OrderType


def test_sut_rebalances(fake_rebalance_context: RebalanceContext, mocker: MockerFixture) -> None:
    """Test rebalance command with fake rebalance context"""

    # given
    runner = CliRunner()

    mocker.patch("pyrb.main._create_rebalance_context", return_value=fake_rebalance_context)

    spy = mocker.spy(fake_rebalance_context.order_manager, "place_order")

    # when
    result = runner.invoke(cli, ["rebalance", "--investment-amount", "1000"], input="y\n")

    # then
    assert result.exit_code == 0
    assert spy.call_count == 2
    assert spy.call_args_list == [
        mocker.call(
            Order(
                symbol="000660",
                price=100,
                quantity=95,
                side="SELL",
                order_type=OrderType.MARKET,
            ),
        ),
        mocker.call(
            Order(
                symbol="005930",
                price=100,
                quantity=70,
                side="SELL",
                order_type=OrderType.MARKET,
            ),
        ),
    ]


def test_sut_rebalances_with_only_buy_orders(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch("pyrb.main._create_rebalance_context", return_value=fake_rebalance_context)

    # when
    result = runner.invoke(cli, ["rebalance", "--investment-amount", "20000"])

    # then
    assert "BUY" in result.output
    assert "SELL" not in result.output


def test_sut_rebalances_with_only_sell_order(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch("pyrb.main._create_rebalance_context", return_value=fake_rebalance_context)

    # when
    result = runner.invoke(cli, ["rebalance", "--investment-amount", "1000"])

    # then
    assert "SELL" in result.output
    assert "BUY" not in result.output


def test_sut_stops_rebalancing_with_disallowance_from_user(
    fake_rebalance_context: RebalanceContext, mocker: MockerFixture
) -> None:
    # given
    runner = CliRunner()

    mocker.patch("pyrb.main._create_rebalance_context", return_value=fake_rebalance_context)

    # when
    result = runner.invoke(cli, ["rebalance", "--investment-amount", "1000"], input="n\n")

    # then
    assert result.exit_code == 0
    assert "No orders were placed" in result.output
