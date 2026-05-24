# Business logic unit tests — mock repository, no database, no HTTP.
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from src.domain.order import Order, OrderItem, OrderStatus
from src.repository.order_repository import OrderRepository
from src.application.services.order_service import OrderService, _NotFound, _Terminal


def make_repo() -> MagicMock:
    return MagicMock(spec=OrderRepository)


def make_order(
    *,
    id: str = "test-id",
    customer_name: str = "Alice",
    status: OrderStatus = OrderStatus.PENDING,
    total: float = 19.98,
) -> Order:
    return Order(
        id=id,
        customer_name=customer_name,
        items=[OrderItem(product_name="Widget", quantity=2, unit_price=9.99)],
        status=status,
        total=total,
        created_at=datetime.now(),
    )


def make_items() -> list[OrderItem]:
    return [OrderItem(product_name="Widget", quantity=2, unit_price=9.99)]


# --- create_order ---

def test_create_order_calculates_total() -> None:
    repo = make_repo()
    repo.add.return_value = make_order(total=19.98)
    svc = OrderService(repo)
    svc.create_order("Alice", make_items())
    added = repo.add.call_args[0][0]
    assert abs(float(added.total) - 19.98) < 0.01


def test_create_order_sets_pending_status() -> None:
    repo = make_repo()
    repo.add.return_value = make_order()
    svc = OrderService(repo)
    svc.create_order("Bob", [OrderItem(product_name="Gadget", quantity=1, unit_price=5.0)])
    added = repo.add.call_args[0][0]
    assert added.status == OrderStatus.PENDING


def test_create_order_generates_id() -> None:
    repo = make_repo()
    repo.add.return_value = make_order()
    svc = OrderService(repo)
    svc.create_order("Carol", [OrderItem(product_name="Thing", quantity=1, unit_price=1.0)])
    added = repo.add.call_args[0][0]
    assert len(added.id) > 0


# --- get_order ---

def test_get_order_returns_none_when_missing() -> None:
    repo = make_repo()
    repo.get.return_value = None
    svc = OrderService(repo)
    assert svc.get_order("nonexistent") is None


# --- delete_order ---

def test_delete_order_returns_false_when_missing() -> None:
    repo = make_repo()
    repo.soft_delete.return_value = None
    svc = OrderService(repo)
    assert svc.delete_order("missing") is False


def test_delete_order_returns_true_when_found() -> None:
    repo = make_repo()
    repo.soft_delete.return_value = make_order()
    svc = OrderService(repo)
    assert svc.delete_order("exists") is True


# --- update_order_status ---

def test_update_order_status_not_found() -> None:
    repo = make_repo()
    repo.get.return_value = None
    svc = OrderService(repo)
    result = svc.update_order_status("missing", OrderStatus.SHIPPED)
    assert isinstance(result, _NotFound)


@pytest.mark.parametrize("terminal_status", [OrderStatus.CANCELLED, OrderStatus.DELIVERED])
def test_update_order_status_terminal(terminal_status: OrderStatus) -> None:
    repo = make_repo()
    repo.get.return_value = make_order(status=terminal_status)
    svc = OrderService(repo)
    result = svc.update_order_status("o1", OrderStatus.SHIPPED)
    assert isinstance(result, _Terminal)


def test_update_order_status_none_payload_returns_order() -> None:
    repo = make_repo()
    repo.get.return_value = make_order()
    svc = OrderService(repo)
    result = svc.update_order_status("o1", None)
    assert isinstance(result, Order)


def test_update_order_status_success() -> None:
    repo = make_repo()
    repo.get.return_value = make_order(status=OrderStatus.PENDING)
    repo.update_status.return_value = make_order(status=OrderStatus.SHIPPED)
    svc = OrderService(repo)
    result = svc.update_order_status("o1", OrderStatus.SHIPPED)
    assert isinstance(result, Order)
    assert result.status == OrderStatus.SHIPPED
