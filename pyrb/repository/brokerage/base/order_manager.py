import abc

from pyrb.model.order import Order


class OrderManager(abc.ABC):
    def __init__(self) -> None: ...

    @abc.abstractmethod
    def place_order(self, order: Order) -> None:
        """
        Places an order with the brokerage. This method should be implemented by the
        concrete class.
        If the order fails to place, an OrderPlacementError should be raised.

        Args:
            order (Order): The order to place.

        Returns:
            None

        Raises:
            OrderPlacementError: If the order fails to place.
        """
        ...
