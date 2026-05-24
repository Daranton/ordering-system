from src.domain.order import OrderStatus

TERMINAL_STATUSES: frozenset[OrderStatus] = frozenset({OrderStatus.CANCELLED, OrderStatus.DELIVERED})
