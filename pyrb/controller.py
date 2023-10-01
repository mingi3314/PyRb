import click
import typer

from pyrb.brokerage.client import TradeMode
from pyrb.brokerage.context import RebalanceContext, create_rebalance_context
from pyrb.brokerage.order_manager import Order
from pyrb.service import (
    get_weight_by_stock,
    prepare_orders,
    validate_investment_amount,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """Rebalance your portfolio"""
    ...


@app.command()
def rebalance(
    investment_amount: float = typer.Option(..., prompt="Enter the total investment amount"),
    brokerage_name: str = typer.Option("ebest", "--brokerage", "-b"),
    trade_mode: TradeMode = typer.Option(TradeMode.PAPER, "--trade-mode", "-t"),
) -> None:
    context = create_rebalance_context(brokerage_name, trade_mode)
    validate_investment_amount(context, investment_amount)

    weight_by_stock = get_weight_by_stock(context.portfolio)
    orders = prepare_orders(context, investment_amount, weight_by_stock)
    user_confirmation = _confirm_orders_to_user(context, orders)

    if user_confirmation:
        _place_orders(context, orders)
    else:
        click.echo("No orders were placed")


def _confirm_orders_to_user(context: RebalanceContext, orders: list[Order]) -> bool:
    """Confirm orders to the user and return the user's confirmation."""
    for order in orders:
        click.echo(f"{order.symbol}: {order.side} {order.quantity} shares @ {order.price}")

    return click.confirm("Do you want to place these orders?")


def _place_orders(context: RebalanceContext, orders: list[Order]) -> None:
    """Place orders and report back to the user."""
    sell_orders = [order for order in orders if order.side == "SELL"]
    buy_orders = [order for order in orders if order.side == "BUY"]

    successful_orders = []
    failed_orders = []

    # Process sell orders first
    click.echo("Processing sell orders first...")
    successful_orders.extend(_process_orders(context, sell_orders))
    failed_orders.extend([order for order in sell_orders if order not in successful_orders])

    # Process buy orders
    click.echo("Processing buy orders...")
    successful_orders.extend(_process_orders(context, buy_orders))
    failed_orders.extend([order for order in buy_orders if order not in successful_orders])

    # Report back to the user
    _report_orders(successful_orders, failed_orders)


def _process_orders(context: RebalanceContext, orders: list[Order]) -> list[Order]:
    """Processes a list of orders and returns a list of successfully placed orders."""
    successful_orders = []

    for order in orders:
        try:
            context.order_manager.place_order(order)
            successful_orders.append(order)
        except Exception as e:
            click.echo(f"Failed to place order for {order.symbol}. Error: {e}")

    return successful_orders


def _report_orders(successful_orders: list[Order], failed_orders: list[Order]) -> None:
    """Provides a summary of successful and failed orders."""
    if successful_orders:
        click.echo("Following orders placed successfully:")
        for order in successful_orders:
            click.echo(f"{order.symbol}: {order.side} {order.quantity} shares")
    if failed_orders:
        click.echo("Following orders failed to place:")
        for order in failed_orders:
            click.echo(f"{order.symbol}: {order.side} {order.quantity} shares")


if __name__ == "__main__":
    app()
