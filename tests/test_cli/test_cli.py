import argparse
import pytest
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import cli.main as cli_main
from src.utils.models import Order, OrderStatus, load_orders, save_orders


@pytest.fixture
def orders_file(tmp_path: Path) -> Iterator[Path]:
    p = tmp_path / "orders.json"
    with patch.object(cli_main, "DATA_FILE", p):
        yield p


def make_args(**kwargs: object) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


# --- cmd_create ---

def test_cmd_create_writes_order(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cli_main.cmd_create(make_args(customer="Alice", item="Widget", quantity=3))
    orders = load_orders(orders_file)
    assert len(orders) == 1
    order = next(iter(orders.values()))
    assert order.customer == "Alice"
    assert order.item == "Widget"
    assert order.quantity == 3
    assert order.status == OrderStatus.PENDING


def test_cmd_create_zero_quantity(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cli_main.cmd_create(make_args(customer="Alice", item="Widget", quantity=0))
    orders = load_orders(orders_file)
    assert next(iter(orders.values())).quantity == 0


def test_cmd_create_prints_id(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cli_main.cmd_create(make_args(customer="Bob", item="Gadget", quantity=1))
    out = capsys.readouterr().out
    assert "Created order" in out


# --- cmd_list ---

def test_cmd_list_empty(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cli_main.cmd_list(make_args(status=None))
    assert "No orders found" in capsys.readouterr().out


def test_cmd_list_shows_orders(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    o = Order(order_id="ord-1", customer="Carol", item="Gizmo", quantity=2)
    save_orders(orders_file, {"ord-1": o})
    cli_main.cmd_list(make_args(status=None))
    out = capsys.readouterr().out
    assert "Carol" in out
    assert "Gizmo" in out


def test_cmd_list_filters_by_status(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    o1 = Order(order_id="o1", customer="Dave", item="A", quantity=1, status=OrderStatus.PENDING)
    o2 = Order(order_id="o2", customer="Eve", item="B", quantity=1, status=OrderStatus.SHIPPED)
    save_orders(orders_file, {"o1": o1, "o2": o2})

    cli_main.cmd_list(make_args(status="shipped"))
    out = capsys.readouterr().out
    assert "Eve" in out
    assert "Dave" not in out


def test_cmd_list_no_filter_shows_all(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    o1 = Order(order_id="o1", customer="Axe", item="A", quantity=1, status=OrderStatus.PENDING)
    o2 = Order(order_id="o2", customer="Bob", item="B", quantity=1, status=OrderStatus.SHIPPED)
    save_orders(orders_file, {"o1": o1, "o2": o2})
    cli_main.cmd_list(make_args(status=None))
    out = capsys.readouterr().out
    assert "Axe" in out
    assert "Bob" in out


def test_cmd_list_no_match_for_filter(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    o = Order(order_id="o1", customer="Frank", item="C", quantity=1, status=OrderStatus.PENDING)
    save_orders(orders_file, {"o1": o})
    cli_main.cmd_list(make_args(status="delivered"))
    out = capsys.readouterr().out
    assert "No orders with status" in out


def test_cmd_list_invalid_status_exits(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    o = Order(order_id="o1", customer="Alice", item="A", quantity=1)
    save_orders(orders_file, {"o1": o})
    with pytest.raises(SystemExit) as exc_info:
        cli_main.cmd_list(make_args(status="nonexistent"))
    assert exc_info.value.code == 1


# --- cmd_get ---

def test_cmd_get_existing_order(orders_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    o = Order(order_id="ord-99", customer="Grace", item="Thing", quantity=4)
    save_orders(orders_file, {"ord-99": o})
    cli_main.cmd_get(make_args(order_id="ord-99"))
    out = capsys.readouterr().out
    assert "Grace" in out


def test_cmd_get_missing_order_exits(orders_file: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_main.cmd_get(make_args(order_id="does-not-exist"))
    assert exc_info.value.code == 1
