import pytest
from datetime import datetime

from src.domain.order import Order, OrderItem, OrderStatus
from src.domain.exceptions import InvalidTransitionError


def make_order(status: OrderStatus = OrderStatus.PENDING) -> Order:
    return Order(
        id="test-id",
        customer_name="Alice",
        items=[OrderItem(product_name="Widget", quantity=1, unit_price=10.0)],
        status=status,
        total=10.0,
        created_at=datetime.now(),
    )


def test_transition_to_updates_status() -> None:
    order = make_order(OrderStatus.PENDING)
    order.transition_to(OrderStatus.CONFIRMED)
    assert order.status == OrderStatus.CONFIRMED


@pytest.mark.parametrize("from_status", [
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED,
    OrderStatus.SHIPPED,
    OrderStatus.DISPUTED,
])
def test_transition_to_from_non_terminal_succeeds(from_status: OrderStatus) -> None:
    order = make_order(from_status)
    order.transition_to(OrderStatus.SHIPPED)
    assert order.status == OrderStatus.SHIPPED


@pytest.mark.parametrize("terminal_status", [OrderStatus.CANCELLED, OrderStatus.DELIVERED])
def test_transition_to_from_terminal_raises(terminal_status: OrderStatus) -> None:
    order = make_order(terminal_status)
    with pytest.raises(InvalidTransitionError) as exc_info:
        order.transition_to(OrderStatus.CONFIRMED)
    assert exc_info.value.current_status == terminal_status
