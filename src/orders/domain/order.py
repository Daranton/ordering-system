from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class OrderItem:
    product_name: str
    quantity: int
    unit_price: float


@dataclass
class Order:
    id: str
    customer_name: str
    status: OrderStatus
    total: float
    created_at: datetime
    items: list[OrderItem]

    def transition_to(self, new_status: OrderStatus) -> None:
        from src.orders.domain.state_machine import TERMINAL_STATUSES
        from src.orders.domain.exceptions import InvalidTransitionError
        if self.status in TERMINAL_STATUSES:
            raise InvalidTransitionError(self.status)
        self.status = new_status
