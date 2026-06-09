from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.orders.domain.order import Order, OrderItem, OrderStatus
from src.orders.infrastructure.db.repositories.order_repository import OrderRepository


def make_order(
    *,
    id: str = "repo-test-id",
    customer_name: str = "Alice",
    status: OrderStatus = OrderStatus.PENDING,
) -> Order:
    return Order(
        id=id,
        customer_name=customer_name,
        items=[OrderItem(product_name="Widget", quantity=2, unit_price=9.99)],
        status=status,
        total=19.98,
        created_at=datetime.now(timezone.utc),
    )


# --- add ---

def test_add_returns_order(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    order = repo.add(make_order(id="add-1"))
    assert order.id == "add-1"
    assert order.customer_name == "Alice"
    assert order.status == OrderStatus.PENDING


def test_add_persists_items(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    order = repo.add(make_order(id="add-2"))
    assert len(order.items) == 1
    assert order.items[0].product_name == "Widget"


# --- get ---

def test_get_returns_order(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    repo.add(make_order(id="get-1"))
    assert repo.get("get-1") is not None


def test_get_returns_none_for_missing(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    assert repo.get("nonexistent") is None


def test_get_excludes_soft_deleted(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    repo.add(make_order(id="get-deleted"))
    repo.soft_delete("get-deleted")
    assert repo.get("get-deleted") is None


# --- list_by_status ---

def test_list_by_status_filters_correctly(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    repo.add(make_order(id="list-pending", status=OrderStatus.PENDING))
    repo.add(make_order(id="list-confirmed", status=OrderStatus.CONFIRMED))
    pending = repo.list_by_status(OrderStatus.PENDING)
    assert any(o.id == "list-pending" for o in pending)
    assert all(o.status == OrderStatus.PENDING for o in pending)


def test_list_by_status_none_returns_all(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    repo.add(make_order(id="list-all-1"))
    repo.add(make_order(id="list-all-2", status=OrderStatus.CONFIRMED))
    ids = {o.id for o in repo.list_by_status(None)}
    assert {"list-all-1", "list-all-2"}.issubset(ids)


def test_list_by_status_excludes_soft_deleted(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    repo.add(make_order(id="list-deleted"))
    repo.soft_delete("list-deleted")
    assert not any(o.id == "list-deleted" for o in repo.list_by_status(None))


# --- soft_delete ---

def test_soft_delete_returns_order(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    repo.add(make_order(id="del-1"))
    result = repo.soft_delete("del-1")
    assert result is not None
    assert result.id == "del-1"


def test_soft_delete_returns_none_for_missing(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    assert repo.soft_delete("nonexistent") is None


# --- update_status ---

def test_update_status_changes_status(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    repo.add(make_order(id="update-1"))
    result = repo.update_status("update-1", OrderStatus.CONFIRMED)
    assert result is not None
    assert result.status == OrderStatus.CONFIRMED


def test_update_status_returns_none_for_missing(db_session: Session) -> None:
    repo = OrderRepository(db_session)
    assert repo.update_status("nonexistent", OrderStatus.CONFIRMED) is None
