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
