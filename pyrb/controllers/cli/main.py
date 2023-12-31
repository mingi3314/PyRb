from pathlib import Path
from typing import Annotated, Literal

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from pyrb.controllers.cli.account import app as account_app
from pyrb.controllers.cli.account import create_account_service
from pyrb.enums import AssetAllocationStrategyEnum, OrderSide
from pyrb.models.order import Order, OrderPlacementResult
from pyrb.repositories.brokerages.context import RebalanceContext, create_rebalance_context
from pyrb.services.rebalance import Rebalancer
from pyrb.services.strategy.asset_allocate import (
    AssetAllocationStrtegyFactory,
)
from pyrb.services.strategy.explicit_target import (
    ExplicitTargetRebalanceStrategy,
    read_targets_from_source,
)
from pyrb.services.strategy.holding_portfolio import HoldingPortfolioRebalanceStrategy

app = typer.Typer()
app.add_typer(account_app, name="account")
console = Console()


@app.callback()
def callback() -> None:
    """Rebalance your portfolio"""
    ...


@app.command()
def holding_portfolio(
    investment_amount: Annotated[float, typer.Option(..., help="The total investment amount")],
) -> None:
    """
    Rebalances a holding portfolio with equal weights based on the specified options.
    """
    context = _create_context()

    strategy = HoldingPortfolioRebalanceStrategy(context)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)
    _place_orders(context, rebalancer, orders)


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
) -> None:
    """
    Rebalances a portfolio with explicit target weights from the specified source.
    Sum of target weights must be 1.0. If not, the weights will be normalized.

    """
    context = _create_context()

    targets = read_targets_from_source(targets_source)
    strategy = ExplicitTargetRebalanceStrategy(targets)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)
    _place_orders(context, rebalancer, orders)


@app.command()
def asset_allocate(
    strategy: Annotated[AssetAllocationStrategyEnum, typer.Option(..., help="The strategy to use")],
    investment_amount: Annotated[float, typer.Option(..., help="The total investment amount")],
) -> None:
    """
    Rebalances a portfolio with the specified asset allocation strategy.

    """
    context = _create_context()

    strategy = AssetAllocationStrtegyFactory().create(strategy)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)
    _place_orders(context, rebalancer, orders)


@app.command()
def portfolio() -> None:
    """
    Display the portfolio table and summary.
    """
    context = _create_context()

    _print_portfolio_table(context)
    _print_portfolio_summary(context)


def _create_context() -> RebalanceContext:
    account_service = create_account_service()
    account = account_service.get()
    context = create_rebalance_context(account)
    return context


def _place_orders(context: RebalanceContext, rebalancer: Rebalancer, orders: list[Order]) -> None:
    """
    Places the given orders using the provided rebalancer.
    Before placing the orders, the user is asked to confirm the orders.
    If the user does not confirm, the orders are not placed.

    Args:
        context (RebalanceContext): The context for rebalancing.
        rebalancer (Rebalancer): The rebalancer object used for placing orders.
        orders (list[Order]): The list of orders to be placed.

    Returns:
        None
    """
    user_confirmation = _get_confirm_for_order_submit(context, orders)
    if not user_confirmation:
        typer.echo("No orders were placed")
        return

    results = rebalancer.place_orders(orders)
    _report_orders(results)


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
            _format(order.quantity, "number"),
            _format(order.price, "currency"),
            _format(total_amount, "currency"),
            _format(current_position_value, "currency"),
            _format(expected_position_value, "currency"),
        )

    console.print(table)

    return typer.confirm("Do you want to place these orders?")


def _report_orders(order_placement_results: list[OrderPlacementResult]) -> None:
    """Provides a summary of successful and failed orders."""
    for res in order_placement_results:
        if res.success:
            typer.echo(f"Successfully placed order: {res.order}")
        else:
            typer.echo(f"Failed to place order: {res.order} ({res.message})")


def _format(value: float, format_type: Literal["number", "currency", "percentage"]) -> str:
    """Format a number."""
    match format_type:
        case "number":
            return f"{value:.2f}"
        case "currency":
            return f"₩{value:,.0f}"
        case "percentage":
            return f"{value:.2%}"
        case _:
            raise NotImplementedError(f"Unsupported format type: {format_type}")


def _print_portfolio_table(context: RebalanceContext) -> None:
    columns = [
        "Symbol",
        "Quantity",
        "Sellable Quantity",
        "Average Buy Price",
        "Total Amount",
        "Return (%)",
    ]

    table = Table(
        box=box.MINIMAL_DOUBLE_HEAD,
        show_header=True,
        header_style="bold magenta",
    )

    for column in columns:
        table.add_column(column, justify="right")

    for position in context.portfolio.positions:
        if position.rtn > 0:
            rtn_style = "red"
        elif position.rtn == 0:
            rtn_style = "black"
        else:
            rtn_style = "green"

        table.add_row(
            position.symbol,
            _format(position.quantity, "number"),
            _format(position.sellable_quantity, "number"),
            _format(position.average_buy_price, "currency"),
            _format(position.total_amount, "currency"),
            Text(_format(position.rtn, "percentage"), style=rtn_style),
        )

    console.print(table)


def _print_portfolio_summary(context: RebalanceContext) -> None:
    cash_balance = context.portfolio.cash_balance
    total_asset_value = sum(p.total_amount for p in context.portfolio.positions)
    total_portfolio_value = total_asset_value + cash_balance

    console.print(Text("\nPortfolio Summary:", style="bold underline"))
    console.print(f"Total Asset Value: {_format(total_asset_value, 'currency')}")
    console.print(f"Cash Balance: {_format(cash_balance, 'currency')}")
    console.print(f"Total Portfolio Value: {_format(total_portfolio_value, 'currency')}")


if __name__ == "__main__":
    app()
