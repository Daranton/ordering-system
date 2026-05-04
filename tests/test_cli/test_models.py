import json
import pytest
from pathlib import Path
from src.utils.models import Order, OrderStatus, load_orders, save_orders


# --- Order dataclass ---

def test_order_defaults() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=3)
    assert o.status == OrderStatus.PENDING
    assert o.amount == 0.0


def test_order_zero_quantity_is_valid() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=0)
    assert o.quantity == 0


def test_order_negative_quantity_raises() -> None:
    with pytest.raises(ValueError, match="quantity cannot be negative"):
        Order(order_id="1", customer="Alice", item="Widget", quantity=-1)


def test_order_invalid_status_raises() -> None:
    with pytest.raises(ValueError, match="not a valid OrderStatus"):
        Order(order_id="1", customer="Alice", item="Widget", quantity=1, status="unknown")  # type: ignore[arg-type]


def test_update_status_valid() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=1)
    o.update_status("shipped")
    assert o.status == OrderStatus.SHIPPED


def test_update_status_accepts_enum_member() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=1)
    o.update_status(OrderStatus.DELIVERED)
    assert o.status == OrderStatus.DELIVERED


def test_update_status_invalid_raises() -> None:
    o = Order(order_id="1", customer="Alice", item="Widget", quantity=1)
    with pytest.raises(ValueError, match="not a valid OrderStatus"):
        o.update_status("broken")


def test_order_status_coerced_from_string_on_load(tmp_path: Path) -> None:
    data = {"z1": {"customer": "Zoe", "item": "X", "quantity": 1, "status": "confirmed", "amount": 0.0}}
    f = tmp_path / "orders.json"
    f.write_text(json.dumps(data))
    orders = load_orders(f)
    assert orders["z1"].status == OrderStatus.CONFIRMED


# --- load_orders ---

def test_load_orders_missing_file(tmp_path: Path) -> None:
    result = load_orders(tmp_path / "nonexistent.json")
    assert result == {}


def test_load_orders_bad_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    result = load_orders(bad)
    assert result == {}


def test_load_orders_json_not_object(tmp_path: Path) -> None:
    f = tmp_path / "orders.json"
    f.write_text("[1, 2, 3]")
    result = load_orders(f)
    assert result == {}


def test_load_orders_invalid_status_skips_entry(tmp_path: Path) -> None:
    data = {
        "bad": {"customer": "X", "item": "Y", "quantity": 1, "status": "bogus", "amount": 0.0},
        "ok": {"customer": "Axe", "item": "Widget", "quantity": 1, "status": "pending", "amount": 0.0},
    }
    f = tmp_path / "orders.json"
    f.write_text(json.dumps(data))
    result = load_orders(f)
    assert "bad" not in result
    assert "ok" in result


def test_load_orders_missing_field_skips_entry(tmp_path: Path) -> None:
    data = {
        "bad": {"item": "Y", "quantity": 1, "status": "pending", "amount": 0.0},  # missing entry "customer"
        "ok": {"customer": "Bobby", "item": "Gadget", "quantity": 2, "status": "pending", "amount": 0.0},
    }
    f = tmp_path / "orders.json"
    f.write_text(json.dumps(data))
    result = load_orders(f)
    assert "bad" not in result
    assert "ok" in result


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
    o = Order(order_id="r1", customer="Dave", item="Thing", quantity=7, status=OrderStatus.SHIPPED)
    save_orders(f, {"r1": o})
    loaded = load_orders(f)
    assert loaded["r1"].customer == "Dave"
    assert loaded["r1"].status == OrderStatus.SHIPPED
    assert loaded["r1"].quantity == 7


def test_save_orders_empty_dict(tmp_path: Path) -> None:
    f = tmp_path / "orders.json"
    save_orders(f, {})
    assert json.loads(f.read_text()) == {}


def test_save_orders_creates_parent_dirs(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "orders.json"
    o = Order(order_id="n1", customer="Eve", item="Part", quantity=1)
    save_orders(nested, {"n1": o})
    assert nested.exists()
