from typing import Literal, cast

import click

from pyrb.client import brokerage_api_client_factory
from pyrb.exceptions import InsufficientFundsException
from pyrb.fetcher import CurrentPrice, PriceFetcher, price_fetcher_factory
from pyrb.order import Order, OrderType
from pyrb.order_manager import OrderManager, order_manager_factory
from pyrb.portfolio import Portfolio, portfolio_factory


class RebalanceContext:
    def __init__(
        self, portfolio: Portfolio, price_fetcher: PriceFetcher, order_manager: OrderManager
    ) -> None:
        self._portfolio = portfolio
        self._price_fetcher = price_fetcher
        self._order_manager = order_manager

    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio

    @property
    def price_fetcher(self) -> PriceFetcher:
        return self._price_fetcher

    @property
    def order_manager(self) -> OrderManager:
        return self._order_manager


@click.group()
@click.pass_context
def cli(ctx: click.Context, brokerage_name: str = "ebest") -> None:
    rebalance_context = _create_rebalance_context(brokerage_name)
    ctx.obj = rebalance_context


@cli.command()
@click.option("--investment-amount", type=float, prompt="Enter the total investment amount")
@click.pass_obj
def rebalance(context: RebalanceContext, investment_amount: float) -> None:
    _validate_investment_amount(context, investment_amount)

    weight_by_stock = _get_weight_by_stock(context.portfolio)
    orders = _prepare_orders(context, investment_amount, weight_by_stock)
    user_confirmation = _confirm_orders_to_user(context, orders)

    if user_confirmation:
        _place_orders(context, orders)
    else:
        click.echo("No orders were placed")


def _validate_investment_amount(context: RebalanceContext, investment_amount: float) -> None:
    if investment_amount > context.portfolio.total_asset:
        raise InsufficientFundsException(
            f"Insufficient funds. The amount of your total asset is {context.portfolio.total_asset}"
        )


def _create_rebalance_context(brokerage_name: str) -> RebalanceContext:
    brokerage_api_client = brokerage_api_client_factory(brokerage_name)

    portfolio = portfolio_factory(brokerage_api_client)
    price_fetcher = price_fetcher_factory(brokerage_api_client)
    order_manager = order_manager_factory(brokerage_api_client)

    rebalance_context = RebalanceContext(portfolio, price_fetcher, order_manager)
    return rebalance_context


def _get_weight_by_stock(portfolio: Portfolio) -> dict[str, float]:
    """return the target weight of each stock"""
    stocks = portfolio.holding_symbols
    return {stock: 1 / len(stocks) for stock in stocks}


def _prepare_orders(
    context: RebalanceContext, investment_amount: float, weight_by_stock: dict[str, float]
) -> list[Order]:
    """Prepare orders to be placed."""
    current_prices = _fetch_current_prices(context, weight_by_stock)
    orders: list[Order] = []

    for stock, weight in weight_by_stock.items():
        current_price = current_prices[stock].price
        current_amount = _get_current_stock_amount(context.portfolio, stock)

        target_amount = investment_amount * weight
        difference_in_amount = target_amount - current_amount
        shares_to_trade = _calculate_shares_to_trade(difference_in_amount, current_price)

        if shares_to_trade != 0:
            order_action = "BUY" if shares_to_trade > 0 else "SELL"
            orders.append(
                Order(
                    symbol=stock,
                    price=current_price,
                    quantity=abs(shares_to_trade),
                    side=cast(Literal["BUY", "SELL"], order_action),
                    order_type=OrderType.MARKET,
                )
            )

    return orders


def _get_current_stock_amount(portfolio: Portfolio, stock: str) -> float:
    """Retrieve the current amount of a stock."""
    current_position = portfolio.get_position(stock)
    return current_position.total_amount if current_position else 0


def _calculate_shares_to_trade(difference_in_amount: float, current_price: float) -> int:
    """Determine the number of shares to trade based on the difference in amount."""
    return int(difference_in_amount / current_price)


def _fetch_current_prices(
    context: RebalanceContext, weight_by_stock: dict[str, float]
) -> dict[str, CurrentPrice]:
    """Fetch the current prices of stocks in the portfolio and target stocks."""
    holding_symbols = context.portfolio.holding_symbols
    target_symbols = weight_by_stock.keys()
    whole_symbols = list(set(holding_symbols).union(target_symbols))
    current_prices = context.price_fetcher.get_current_prices(whole_symbols)
    return current_prices


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
    cli()
