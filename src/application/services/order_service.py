from datetime import datetime, timezone

from src.domain.order import Order, OrderItem, OrderStatus
from src.domain.repository import OrderRepositoryProtocol
from src.domain.ids import generate_order_id
from src.domain.exceptions import InvalidTransitionError, OrderNotFoundError


class OrderService:
    def __init__(self, repo: OrderRepositoryProtocol) -> None:
        self._repo = repo

    def create_order(self, customer_name: str, items: list[OrderItem]) -> Order:
        total = sum(item.quantity * item.unit_price for item in items)
        order = Order(
            id=generate_order_id(),
            customer_name=customer_name,
            items=items,
            status=OrderStatus.PENDING,
            total=total,
            created_at=datetime.now(timezone.utc),
        )
        return self._repo.add(order)

    def get_order(self, order_id: str) -> Order | None:
        return self._repo.get(order_id)

    def list_orders(self, status: OrderStatus | None) -> list[Order]:
        return self._repo.list_by_status(status)

    def delete_order(self, order_id: str) -> bool:
        return self._repo.soft_delete(order_id) is not None

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> Order:
        order = self._repo.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        order.transition_to(new_status)
        updated = self._repo.update_status(order_id, new_status)
        if updated is None:
            raise OrderNotFoundError(order_id)
        return updated
