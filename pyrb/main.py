from typing import Literal, cast

import click

from pyrb.fetcher import PriceFetcher, price_fetcher_factory
from pyrb.order_manager import Order, OrderManager, OrderType, order_manager_factory
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
    portfolio = portfolio_factory(brokerage_name)
    price_fetcher = price_fetcher_factory(brokerage_name)
    order_manager = order_manager_factory(brokerage_name)

    ctx.obj = RebalanceContext(portfolio, price_fetcher, order_manager)


@cli.command()
@click.option("--investment", type=float, prompt="Enter the total investment amount")
@click.pass_obj
def rebalance(context: RebalanceContext, investment: float) -> None:
    weights = _get_weights(context.portfolio)

    orders: list[Order] = []

    # Get current prices for all holding symbols
    holding_symbols = context.portfolio.holding_symbols
    current_prices = context.price_fetcher.get_current_prices(holding_symbols)

    for stock, weight in weights.items():
        target_amount = investment * weight

        # Get current stock price
        current_price = current_prices[stock].price

        # Get the current holding quantity of the stock
        current_position = next(p for p in context.portfolio.positions if p.symbol == stock)
        current_quantity = current_position.quantity
        current_investment = current_price * current_quantity

        # Calculate the difference to find out how much to buy/sell
        difference_in_amount = target_amount - current_investment

        # Calculate the number of shares to buy/sell
        shares_to_trade = round(difference_in_amount / current_price)

        if shares_to_trade > 0:
            action = "BUY"
        elif shares_to_trade < 0:
            action = "SELL"
            shares_to_trade = abs(shares_to_trade)
        else:
            continue  # No need to place an order if no change is needed

        orders.append(
            Order(
                symbol=stock,
                price=current_price,
                quantity=shares_to_trade,
                side=cast(Literal["BUY", "SELL"], action),
                order_type=OrderType.MARKET,
            )
        )

    # Confirm with the user
    for order in orders:
        click.echo(f"{order.symbol}: {order.side} {order.quantity} shares @ {order.price}")
    if click.confirm("Do you want to execute these orders?"):
        for order in orders:
            # Pseudo-code: Implement actual logic to send orders to the broker
            context.order_manager.place_order(order)

        click.echo("Orders placed successfully!")
    else:
        click.echo("Orders not executed.")


def _get_weights(portfolio: Portfolio) -> dict[str, float]:
    stocks = portfolio.holding_symbols
    return {stock: 1 / len(stocks) for stock in stocks}


if __name__ == "__main__":
    cli()
