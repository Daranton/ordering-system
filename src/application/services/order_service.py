from datetime import datetime, timezone
from typing import TypeAlias

from src.api.schemas import OrderCreate, OrderItemSchema, OrderResponse, OrderUpdate
from src.domain.order import Order, OrderItem, OrderStatus
from src.repository.order_repository import OrderRepository
from src.utils.ids import generate_order_id

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
        order = Order(
            id=generate_order_id(),
            customer_name=payload.customer_name,
            items=[
                OrderItem(
                    product_name=i.product_name,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                )
                for i in payload.items
            ],
            status=OrderStatus.PENDING,
            total=total,
            created_at=datetime.now(timezone.utc),
        )
        return _to_response(self._repo.add(order))

    def get_order(self, order_id: str) -> OrderResponse | None:
        order = self._repo.get(order_id)
        return _to_response(order) if order is not None else None

    def list_orders(self, status: OrderStatus | None) -> list[OrderResponse]:
        return [_to_response(o) for o in self._repo.list_by_status(status)]

    def delete_order(self, order_id: str) -> bool:
        return self._repo.soft_delete(order_id) is not None

    def update_order_status(self, order_id: str, payload: OrderUpdate) -> UpdateResult:
        order = self._repo.get(order_id)
        if order is None:
            return _NotFound()
        if order.status in TERMINAL_STATUSES:
            return _Terminal(order.status)
        if payload.status is None:
            return _to_response(order)
        updated = self._repo.update_status(order_id, payload.status)
        if updated is None:
            return _NotFound()
        return _to_response(updated)


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=[
            OrderItemSchema(
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ],
    )
