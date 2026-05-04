from functools import lru_cache

from src.api.schemas import OrderResponse


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

    def update(self, order: OrderResponse) -> OrderResponse:
        # TODO: guard against missing order.id
        self._orders[order.id] = order
        return order


@lru_cache
def get_repository() -> OrderRepository:
    return OrderRepository()
