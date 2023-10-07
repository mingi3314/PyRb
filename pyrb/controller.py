import typer

from pyrb.brokerage.base.client import TradeMode
from pyrb.brokerage.base.order_manager import Order, OrderStatus
from pyrb.brokerage.context import RebalanceContext, create_rebalance_context
from pyrb.brokerage.factory import BrokerageType
from pyrb.service.rebalance import Rebalancer
from pyrb.service.strategy.holding_portfolio import HoldingPortfolioRebalanceStrategy

app = typer.Typer()


@app.callback()
def callback() -> None:
    """Rebalance your portfolio"""
    ...


@app.command()
def holding_portfolio(
    investment_amount: float = typer.Option(..., help="The total investment amount"),
    brokerage: BrokerageType = typer.Option(
        BrokerageType.EBEST, help="The name of the brokerage to use"
    ),
    trade_mode: TradeMode = typer.Option(TradeMode.PAPER, help="The trade mode to use"),
) -> None:
    """
    Rebalances a holding portfolio with equal weights based on the specified options.
    """
    context = create_rebalance_context(brokerage, trade_mode)
    strategy = HoldingPortfolioRebalanceStrategy(context)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount)
    user_confirmation = _get_confirm_for_order_submit(context, orders)

    if user_confirmation:
        rebalancer.place_orders(orders)
    else:
        typer.echo("No orders were placed")

    _report_orders(orders)


def _get_confirm_for_order_submit(context: RebalanceContext, orders: list[Order]) -> bool:
    """Confirm orders to the user and return the user's confirmation."""
    for order in orders:
        typer.echo(f"{order.symbol}: {order.side} {order.quantity} shares @ {order.price}")

    return typer.confirm("Do you want to place these orders?")


def _report_orders(orders: list[Order]) -> None:
    """Provides a summary of successful and failed orders."""
    for order in orders:
        if order.status == OrderStatus.PLACED:
            typer.echo(f"Successfully placed order: {order}")
        elif order.status == OrderStatus.REJECTED:
            typer.echo(f"Failed to place order: {order}")


if __name__ == "__main__":
    app()
