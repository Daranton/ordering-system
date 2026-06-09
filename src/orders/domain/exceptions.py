from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.order import OrderStatus


class OrderNotFoundError(Exception):
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' not found")


class InvalidTransitionError(Exception):
    def __init__(self, current_status: OrderStatus) -> None:
        self.current_status = current_status
        super().__init__(f"Order in terminal state '{current_status}' cannot be updated")
