import json
import pytest
from pathlib import Path
from src.utils.models import Order, load_orders, save_orders


# --- Order dataclass ---

def test_order_defaults() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=3)
    assert o.status == "pending"
    assert o.amount == 0.0


def test_order_negative_quantity_raises() -> None:
    with pytest.raises(ValueError, match="quantity cannot be negative"):
        Order(order_id="1", customer="Alice", item="Widget", quantity=-1)


def test_order_invalid_status_raises() -> None:
    with pytest.raises(ValueError, match="invalid status"):
        Order(order_id="1", customer="Alice", item="Widget", quantity=1, status="unknown")


def test_update_status_valid() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=1)
    o.update_status("shipped")
    assert o.status == "shipped"


def test_update_status_invalid_raises() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=1)
    with pytest.raises(ValueError, match="invalid status"):
        o.update_status("broken")


# --- load_orders ---

def test_load_orders_missing_file(tmp_path: Path) -> None:
    result = load_orders(tmp_path / "nonexistent.json")
    assert result == {}


def test_load_orders_bad_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    result = load_orders(bad)
    assert result == {}


def test_load_orders_valid(tmp_path: Path) -> None:
    data = {
        "abc": {"customer": "Bob", "item": "Gadget", "quantity": 2, "status": "pending", "amount": 0.0}
    }
    f = tmp_path / "orders.json"
    f.write_text(json.dumps(data))
    orders = load_orders(f)
    assert "abc" in orders
    assert orders["abc"].customer == "Bob"
    assert orders["abc"].quantity == 2


# --- save_orders ---

def test_save_orders_writes_file(tmp_path: Path) -> None:
    o = Order(order_id="x1", customer="Carol", item="Gizmo", quantity=5)
    save_orders(tmp_path / "orders.json", {"x1": o})
    data = json.loads((tmp_path / "orders.json").read_text())
    assert "x1" in data
    assert data["x1"]["customer"] == "Carol"
    assert data["x1"]["quantity"] == 5


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    f = tmp_path / "orders.json"
    o = Order(order_id="r1", customer="Dave", item="Thing", quantity=7, status="shipped")
    save_orders(f, {"r1": o})
    loaded = load_orders(f)
    assert loaded["r1"].customer == "Dave"
    assert loaded["r1"].status == "shipped"
    assert loaded["r1"].quantity == 7


def test_save_orders_creates_parent_dirs(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "orders.json"
    o = Order(order_id="n1", customer="Eve", item="Part", quantity=1)
    save_orders(nested, {"n1": o})
    assert nested.exists()
