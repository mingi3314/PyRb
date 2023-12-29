from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from pyrb.controller.cli.account import APP_NAME
from pyrb.controller.cli.account import app as account_app
from pyrb.enums import AssetAllocationStrategyEnum, OrderSide
from pyrb.model.order import Order, OrderPlacementResult
from pyrb.repository.account import LocalConfigAccountRepository
from pyrb.repository.brokerage.context import RebalanceContext, create_rebalance_context
from pyrb.service.account import AccountService
from pyrb.service.rebalance import Rebalancer
from pyrb.service.strategy.asset_allocate import (
    AssetAllocationStrtegyFactory,
)
from pyrb.service.strategy.explicit_target import (
    ExplicitTargetRebalanceStrategy,
    read_targets_from_source,
)
from pyrb.service.strategy.holding_portfolio import HoldingPortfolioRebalanceStrategy

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
    app_config_dir = Path(typer.get_app_dir(APP_NAME))
    accounts_config_path = app_config_dir / "accounts"

    account_service = AccountService(
        account_repo=LocalConfigAccountRepository(accounts_config_path)
    )

    account = account_service.get()
    context = create_rebalance_context(account)
    strategy = HoldingPortfolioRebalanceStrategy(context)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)

    user_confirmation = _get_confirm_for_order_submit(context, orders)
    if not user_confirmation:
        typer.echo("No orders were placed")

    results = rebalancer.place_orders(orders)
    _report_orders(results)


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
    app_config_dir = Path(typer.get_app_dir(APP_NAME))
    accounts_config_path = app_config_dir / "accounts"

    account_service = AccountService(
        account_repo=LocalConfigAccountRepository(accounts_config_path)
    )

    account = account_service.get()
    context = create_rebalance_context(account)
    targets = read_targets_from_source(targets_source)
    strategy = ExplicitTargetRebalanceStrategy(targets)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)

    user_confirmation = _get_confirm_for_order_submit(context, orders)
    if not user_confirmation:
        typer.echo("No orders were placed")

    results = rebalancer.place_orders(orders)
    _report_orders(results)


@app.command()
def asset_allocate(
    strategy: Annotated[AssetAllocationStrategyEnum, typer.Option(..., help="The strategy to use")],
    investment_amount: Annotated[float, typer.Option(..., help="The total investment amount")],
) -> None:
    """
    Rebalances a portfolio with the specified asset allocation strategy.

    """
    app_config_dir = Path(typer.get_app_dir(APP_NAME))
    accounts_config_path = app_config_dir / "accounts"

    account_service = AccountService(
        account_repo=LocalConfigAccountRepository(accounts_config_path)
    )

    account = account_service.get()
    context = create_rebalance_context(account)

    strategy = AssetAllocationStrtegyFactory().create(strategy)
    rebalancer = Rebalancer(context, strategy)

    orders = rebalancer.prepare_orders(investment_amount=investment_amount)

    user_confirmation = _get_confirm_for_order_submit(context, orders)
    if not user_confirmation:
        typer.echo("No orders were placed")

    results = rebalancer.place_orders(orders)
    _report_orders(results)


@app.command()
def portfolio() -> None:
    app_config_dir = Path(typer.get_app_dir(APP_NAME))
    accounts_config_path = app_config_dir / "accounts"

    account_service = AccountService(
        account_repo=LocalConfigAccountRepository(accounts_config_path)
    )

    account = account_service.get()
    context = create_rebalance_context(account)

    table = Table(
        "Symbol",
        "Quantity",
        "Sellable Quantity",
        "Average Buy Price",
        "Total Amount",
        "Return (%)",
    )

    for position in context.portfolio.positions:
        table.add_row(
            position.symbol,
            str(position.quantity),
            str(position.sellable_quantity),
            str(position.average_buy_price),
            str(position.total_amount),
            str(position.rtn),
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


def _report_orders(order_placement_results: list[OrderPlacementResult]) -> None:
    """Provides a summary of successful and failed orders."""
    for res in order_placement_results:
        if res.success:
            typer.echo(f"Successfully placed order: {res.order}")
        else:
            typer.echo(f"Failed to place order: {res.order} ({res.message})")


if __name__ == "__main__":
    app()
