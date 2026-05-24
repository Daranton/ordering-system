from datetime import datetime, timezone
from typing import TypeAlias

from src.api.schemas import OrderCreate, OrderResponse, OrderUpdate
from src.repository.order_repository import OrderRepository
from src.utils.ids import generate_order_id
from src.utils.models import OrderStatus

TERMINAL_STATUSES: frozenset[OrderStatus] = frozenset({OrderStatus.CANCELLED, OrderStatus.DELIVERED})


class _NotFound:
    pass


class _Terminal:
    def __init__(self, status: OrderStatus) -> None:
        self.status = status


UpdateResult: TypeAlias = OrderResponse | _NotFound | _Terminal


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def create_order(self, payload: OrderCreate) -> OrderResponse:
        total = sum(item.quantity * item.unit_price for item in payload.items)
        order = OrderResponse(
            id=generate_order_id(),
            customer_name=payload.customer_name,
            items=payload.items,
            status=OrderStatus.PENDING,
            total=total,
            created_at=datetime.now(timezone.utc),
        )
        return self._repo.add(order)
    
    # get, list, delete are thin delegations to the repository. 
    def get_order(self, order_id: str) -> OrderResponse | None:
        return self._repo.get(order_id)

    def list_orders(self, status: OrderStatus | None) -> list[OrderResponse]:
        return self._repo.list_by_status(status)

    def delete_order(self, order_id: str) -> bool:
        return self._repo.soft_delete(order_id) is not None

    def update_order_status(self, order_id: str, payload: OrderUpdate) -> UpdateResult:
        order = self._repo.get(order_id)
        if order is None:
            return _NotFound()
        if order.status in TERMINAL_STATUSES:
            return _Terminal(order.status)
        if payload.status is None:
            return order
        updated = self._repo.update_status(order_id, payload.status)
        if updated is None:
            return _NotFound()
        return updated
