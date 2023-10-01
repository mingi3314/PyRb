from typing import Literal, cast

from pyrb.brokerage.context import RebalanceContext
from pyrb.brokerage.fetcher import CurrentPrice
from pyrb.brokerage.order_manager import (
    Order,
    OrderType,
)
from pyrb.brokerage.portfolio import Portfolio
from pyrb.exceptions import InsufficientFundsException


def validate_investment_amount(context: RebalanceContext, investment_amount: float) -> None:
    if investment_amount > context.portfolio.total_asset:
        raise InsufficientFundsException(
            f"Insufficient funds. The amount of your total asset is {context.portfolio.total_asset}"
        )


def get_weight_by_stock(portfolio: Portfolio) -> dict[str, float]:
    """return the target weight of each stock"""
    stocks = portfolio.holding_symbols
    return {stock: 1 / len(stocks) for stock in stocks}


def _calculate_shares_to_trade(difference_in_amount: float, current_price: float) -> int:
    """Determine the number of shares to trade based on the difference in amount."""
    return int(difference_in_amount / current_price)


def _get_current_stock_amount(portfolio: Portfolio, stock: str) -> float:
    """Retrieve the current amount of a stock."""
    current_position = portfolio.get_position(stock)
    return current_position.total_amount if current_position else 0


def _fetch_current_prices(
    context: RebalanceContext, weight_by_stock: dict[str, float]
) -> dict[str, CurrentPrice]:
    """Fetch the current prices of stocks in the portfolio and target stocks."""
    holding_symbols = context.portfolio.holding_symbols
    target_symbols = weight_by_stock.keys()
    whole_symbols = list(set(holding_symbols).union(target_symbols))
    current_prices = context.price_fetcher.get_current_prices(whole_symbols)
    return current_prices


def prepare_orders(
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
