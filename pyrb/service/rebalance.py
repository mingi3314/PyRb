from math import floor

from pyrb.brokerage.base.fetcher import CurrentPrice
from pyrb.brokerage.base.order_manager import (
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
)
from pyrb.brokerage.base.portfolio import Portfolio
from pyrb.brokerage.context import RebalanceContext
from pyrb.exceptions import InsufficientFundsException, OrderPlacementError
from pyrb.service.strategy.base import Strategy


class Rebalancer:
    def __init__(self, context: RebalanceContext, strategy: Strategy) -> None:
        self._context = context
        self._strategy = strategy

    def prepare_orders(self, investment_amount: float) -> list[Order]:
        """
        Prepare a list of orders to rebalance the portfolio based on the given investment amount.
        If the investment amount is greater than the total value of the portfolio, an exception
        will be raised.

        Args:
            investment_amount : The amount of money to invest in the portfolio.

        Returns:
            list[Order]: A list of orders to rebalance the portfolio.
        """

        def _calculate_shares_to_trade(difference_in_amount: float, current_price: float) -> int:
            """Determine the number of shares to trade based on the difference in amount."""
            return floor(difference_in_amount / current_price)

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

        self._validate_investment_amount(investment_amount)

        weight_by_stock = self._strategy.create_target_weights()

        current_prices = _fetch_current_prices(self._context, weight_by_stock)
        orders: list[Order] = []

        for stock, weight in weight_by_stock.items():
            current_price = current_prices[stock].price
            current_amount = _get_current_stock_amount(self._context.portfolio, stock)

            target_amount = investment_amount * weight
            difference_in_amount = target_amount - current_amount
            shares_to_trade = _calculate_shares_to_trade(difference_in_amount, current_price)

            if shares_to_trade != 0:
                order_action = OrderSide.BUY if shares_to_trade > 0 else OrderSide.SELL
                orders.append(
                    Order(
                        symbol=stock,
                        price=current_price,
                        quantity=abs(shares_to_trade),
                        side=order_action,
                        order_type=OrderType.MARKET,
                    )
                )

        # 매도주문을 우선 제출
        orders.sort(key=lambda order: order.side == OrderSide.SELL, reverse=True)
        return orders

    def place_orders(self, orders: list[Order]) -> None:
        """
        Place a list of orders in the market.
        The status of each order will be updated based on the result of the order placement.

        Args:
            orders (list[Order]): A list of orders to be placed in the market.

        Returns:
            None
        """
        for order in orders:
            try:
                self._context.order_manager.place_order(order)
                order.status = OrderStatus.PLACED

            except OrderPlacementError:
                order.status = OrderStatus.REJECTED  # TODO: handle rejected orders

    def _validate_investment_amount(self, investment_amount: float) -> None:
        if investment_amount > self._context.portfolio.total_value:
            raise InsufficientFundsException(
                "Insufficient funds. The amount of your total asset is"
                f" {self._context.portfolio.total_value}"
            )
