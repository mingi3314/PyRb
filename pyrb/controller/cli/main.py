from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from pyrb.repository.brokerage.base.client import TradeMode
from pyrb.repository.brokerage.base.order_manager import Order, OrderSide, OrderStatus
from pyrb.repository.brokerage.context import RebalanceContext, create_rebalance_context
from pyrb.repository.brokerage.factory import BrokerageType
from pyrb.service.rebalance import Rebalancer
from pyrb.service.strategy.asset_allocate import (
    AssetAllocationStrategyEnum,
    AssetAllocationStrtegyFactory,
)
from pyrb.service.strategy.explicit_target import (
    ExplicitTargetRebalanceStrategy,
    read_targets_from_source,
)
from pyrb.service.strategy.holding_portfolio import HoldingPortfolioRebalanceStrategy

app = typer.Typer()
console = Console()


@app.callback()
def callback() -> None:
    """Rebalance your portfolio"""
    ...


@app.command()
def holding_portfolio(
    investment_amount: Annotated[float, typer.Option(..., help="The total investment amount")],
    brokerage: Annotated[
        BrokerageType, typer.Option(help="The name of the brokerage to use")
    ] = BrokerageType.EBEST,
    trade_mode: Annotated[TradeMode, typer.Option(help="The trade mode to use")] = TradeMode.PAPER,
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


@app.command()
def explicit_target(
    targets_source: Annotated[
        Path,
        typer.Option(
            ...,
            help=(
                "The source to read the target weights from. Supported file types: .csv, .json,"
                " .yaml"
            ),  # TODO: add docstring for each file structure.
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    investment_amount: Annotated[float, typer.Option(..., help="The total investment amount")],
    brokerage: Annotated[
        BrokerageType, typer.Option(help="The name of the brokerage to use")
    ] = BrokerageType.EBEST,
    trade_mode: Annotated[TradeMode, typer.Option(help="The trade mode to use")] = TradeMode.PAPER,
) -> None:
    """
    Rebalances a portfolio with explicit target weights from the specified source.
    Sum of target weights must be 1.0. If not, the weights will be normalized.

    """
    context = create_rebalance_context(brokerage, trade_mode)
    targets = read_targets_from_source(targets_source)
    strategy = ExplicitTargetRebalanceStrategy(targets)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)
    user_confirmation = _get_confirm_for_order_submit(context, orders)

    if user_confirmation:
        rebalancer.place_orders(orders)
    else:
        typer.echo("No orders were placed")

    _report_orders(orders)


@app.command()
def asset_allocate(
    strategy: Annotated[AssetAllocationStrategyEnum, typer.Option(..., help="The strategy to use")],
    investment_amount: Annotated[float, typer.Option(..., help="The total investment amount")],
    brokerage: Annotated[
        BrokerageType, typer.Option(help="The name of the brokerage to use")
    ] = BrokerageType.EBEST,
    trade_mode: Annotated[TradeMode, typer.Option(help="The trade mode to use")] = TradeMode.PAPER,
) -> None:
    """
    Rebalances a portfolio with the specified asset allocation strategy.

    """
    context = create_rebalance_context(brokerage, trade_mode)
    strategy = AssetAllocationStrtegyFactory().create(strategy)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)
    user_confirmation = _get_confirm_for_order_submit(context, orders)

    if user_confirmation:
        rebalancer.place_orders(orders)
    else:
        typer.echo("No orders were placed")

    _report_orders(orders)


@app.command()
def portfolio(
    brokerage: Annotated[
        BrokerageType, typer.Option(help="The name of the brokerage to use")
    ] = BrokerageType.EBEST,
    trade_mode: Annotated[TradeMode, typer.Option(help="The trade mode to use")] = TradeMode.PAPER,
) -> None:
    context = create_rebalance_context(brokerage, trade_mode)
    context.portfolio.refresh()

    table = Table("Symbol", "Quantity", "Sellable Quantity", "Average Buy Price", "Total Amount")

    for position in context.portfolio.positions:
        table.add_row(
            position.symbol,
            str(position.quantity),
            str(position.sellable_quantity),
            str(position.average_buy_price),
            str(position.total_amount),
        )

    console.print(table)


def _get_confirm_for_order_submit(context: RebalanceContext, orders: list[Order]) -> bool:
    """Confirm orders to the user and return the user's confirmation."""
    table = Table(
        "Symbol",
        "Side",
        "Quantity",
        "Price",
        "Total Amount",
        "Current position value",
        "Expected position value",
    )

    for order in orders:
        total_amount = order.quantity * order.price
        current_position_value = context.portfolio.get_position_amount(order.symbol)
        expected_position_value = (
            current_position_value + total_amount
            if order.side == OrderSide.BUY
            else current_position_value - total_amount
        )

        table.add_row(
            order.symbol,
            order.side,
            str(order.quantity),
            str(order.price),
            str(total_amount),
            str(current_position_value),
            str(expected_position_value),
        )

    console.print(table)

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
