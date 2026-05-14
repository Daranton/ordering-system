# Business logic unit tests — mock repository, no database, no HTTP.
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from src.api.schemas import OrderCreate, OrderItemSchema, OrderResponse, OrderUpdate
from src.repository.order_repository import OrderRepository
from src.service.order_service import OrderService, _NotFound, _Terminal
from src.utils.models import OrderStatus


def make_repo() -> MagicMock:
    return MagicMock(spec=OrderRepository)


def make_order_response(
    *,
    id: str = "test-id",
    customer_name: str = "Alice",
    status: OrderStatus = OrderStatus.PENDING,
    total: float = 19.98,
) -> OrderResponse:
    return OrderResponse(
        id=id,
        customer_name=customer_name,
        items=[OrderItemSchema(product_name="Widget", quantity=2, unit_price=9.99)],
        status=status,
        total=total,
        created_at=datetime.now(),
    )


# --- create_order ---

def test_create_order_calculates_total() -> None:
    repo = make_repo()
    repo.add.return_value = make_order_response(total=19.98)
    svc = OrderService(repo)
    payload = OrderCreate(
        customer_name="Alice",
        items=[OrderItemSchema(product_name="Widget", quantity=2, unit_price=9.99)],
    )
    svc.create_order(payload)
    added = repo.add.call_args[0][0]
    assert abs(float(added.total) - 19.98) < 0.01


def test_create_order_sets_pending_status() -> None:
    repo = make_repo()
    repo.add.return_value = make_order_response()
    svc = OrderService(repo)
    payload = OrderCreate(
        customer_name="Bob",
        items=[OrderItemSchema(product_name="Gadget", quantity=1, unit_price=5.0)],
    )
    svc.create_order(payload)
    added = repo.add.call_args[0][0]
    assert added.status == OrderStatus.PENDING


def test_create_order_generates_id() -> None:
    repo = make_repo()
    repo.add.return_value = make_order_response()
    svc = OrderService(repo)
    payload = OrderCreate(
        customer_name="Carol",
        items=[OrderItemSchema(product_name="Thing", quantity=1, unit_price=1.0)],
    )
    svc.create_order(payload)
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
    repo.soft_delete.return_value = make_order_response()
    svc = OrderService(repo)
    assert svc.delete_order("exists") is True


# --- update_order_status ---

def test_update_order_status_not_found() -> None:
    repo = make_repo()
    repo.get.return_value = None
    svc = OrderService(repo)
    result = svc.update_order_status("missing", OrderUpdate(status=OrderStatus.SHIPPED))
    assert isinstance(result, _NotFound)


@pytest.mark.parametrize("terminal_status", [OrderStatus.CANCELLED, OrderStatus.DELIVERED])
def test_update_order_status_terminal(terminal_status: OrderStatus) -> None:
    repo = make_repo()
    repo.get.return_value = make_order_response(status=terminal_status)
    svc = OrderService(repo)
    result = svc.update_order_status("o1", OrderUpdate(status=OrderStatus.SHIPPED))
    assert isinstance(result, _Terminal)


def test_update_order_status_none_payload_returns_order() -> None:
    order = make_order_response()
    repo = make_repo()
    repo.get.return_value = order
    svc = OrderService(repo)
    result = svc.update_order_status("o1", OrderUpdate(status=None))
    assert result == order


def test_update_order_status_success() -> None:
    original = make_order_response(status=OrderStatus.PENDING)
    updated = make_order_response(status=OrderStatus.SHIPPED)
    repo = make_repo()
    repo.get.return_value = original
    repo.update_status.return_value = updated
    svc = OrderService(repo)
    result = svc.update_order_status("o1", OrderUpdate(status=OrderStatus.SHIPPED))
    assert isinstance(result, OrderResponse)
    assert result.status == OrderStatus.SHIPPED
