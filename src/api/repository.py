from functools import lru_cache

from src.api.schemas import OrderResponse
from src.utils.models import OrderStatus


class OrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, OrderResponse] = {}

    def add(self, order: OrderResponse) -> OrderResponse:
        # TODO: guard against duplicate order.id
        self._orders[order.id] = order
        return order

    def get(self, order_id: str) -> OrderResponse | None:
        return self._orders.get(order_id)

    def list_all(self) -> list[OrderResponse]:
        return list(self._orders.values())

    def list_by_status(self, status: OrderStatus | None) -> list[OrderResponse]:
        if status is None:
            return self.list_all()
        return [o for o in self._orders.values() if o.status == status]

    def update(self, order: OrderResponse) -> OrderResponse:
        # TODO: guard against missing order.id
        self._orders[order.id] = order
        return order


@lru_cache
def get_repository() -> OrderRepository:
    return OrderRepository()
