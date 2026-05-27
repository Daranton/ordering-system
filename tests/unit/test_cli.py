# Presentation layer tests — verifies CLI sends correct requests and handles responses.
import argparse
import pytest
from unittest.mock import MagicMock, patch

import cli.main as cli_main


def make_args(**kwargs: object) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def mock_response(status_code: int = 200, json_data: object = None) -> MagicMock:
    r = MagicMock()
    r.status_code = status_code
    r.json.return_value = json_data
    r.raise_for_status.return_value = None
    return r


# --- cmd_create ---

def test_cmd_create_prints_id(capsys: pytest.CaptureFixture[str]) -> None:
    resp = mock_response(201, {"id": "test-id-123"})
    with patch("httpx.post", return_value=resp):
        cli_main.cmd_create(make_args(customer="Alice", item="Widget", quantity=2, unit_price=9.99))
    assert "test-id-123" in capsys.readouterr().out


def test_cmd_create_sends_correct_payload() -> None:
    resp = mock_response(201, {"id": "abc"})
    with patch("httpx.post", return_value=resp) as mock_post:
        cli_main.cmd_create(make_args(customer="Bob", item="Gadget", quantity=3, unit_price=5.0))
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["customer_name"] == "Bob"
    assert payload["items"][0]["product_name"] == "Gadget"
    assert payload["items"][0]["quantity"] == 3
    assert payload["items"][0]["unit_price"] == 5.0


# --- cmd_list ---

def test_cmd_list_empty(capsys: pytest.CaptureFixture[str]) -> None:
    resp = mock_response(200, [])
    with patch("httpx.get", return_value=resp):
        cli_main.cmd_list(make_args(status=None))
    assert "No orders found" in capsys.readouterr().out


def test_cmd_list_shows_orders(capsys: pytest.CaptureFixture[str]) -> None:
    orders = [{"id": "o1", "customer_name": "Carol", "status": "pending", "total": 10.0}]
    resp = mock_response(200, orders)
    with patch("httpx.get", return_value=resp):
        cli_main.cmd_list(make_args(status=None))
    assert "Carol" in capsys.readouterr().out


def test_cmd_list_filters_by_status(capsys: pytest.CaptureFixture[str]) -> None:
    resp = mock_response(200, [{"id": "o2", "customer_name": "Eve", "status": "shipped", "total": 5.0}])
    with patch("httpx.get", return_value=resp) as mock_get:
        cli_main.cmd_list(make_args(status="shipped"))
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["status"] == "shipped"


def test_cmd_list_invalid_status_exits(capsys: pytest.CaptureFixture[str]) -> None:
    resp = mock_response(422, {"detail": "Invalid status"})
    with patch("httpx.get", return_value=resp):
        with pytest.raises(SystemExit) as exc_info:
            cli_main.cmd_list(make_args(status="nonexistent"))
    assert exc_info.value.code == 1


# --- cmd_get ---

def test_cmd_get_existing_order(capsys: pytest.CaptureFixture[str]) -> None:
    order = {"id": "ord-99", "customer_name": "Grace", "status": "pending", "total": 0.0, "items": []}
    resp = mock_response(200, order)
    with patch("httpx.get", return_value=resp):
        cli_main.cmd_get(make_args(order_id="ord-99"))
    assert "Grace" in capsys.readouterr().out


def test_cmd_get_missing_order_exits() -> None:
    resp = mock_response(404, {"detail": "Not found"})
    with patch("httpx.get", return_value=resp):
        with pytest.raises(SystemExit) as exc_info:
            cli_main.cmd_get(make_args(order_id="does-not-exist"))
    assert exc_info.value.code == 1


# --- cmd_update_status ---

def test_cmd_update_status_success(capsys: pytest.CaptureFixture[str]) -> None:
    resp = mock_response(200, {"id": "o1", "status": "shipped"})
    with patch("httpx.patch", return_value=resp):
        cli_main.cmd_update_status(make_args(order_id="o1", status="shipped"))
    assert "shipped" in capsys.readouterr().out


def test_cmd_update_status_not_found_exits() -> None:
    resp = mock_response(404, {"detail": "Not found"})
    with patch("httpx.patch", return_value=resp):
        with pytest.raises(SystemExit) as exc_info:
            cli_main.cmd_update_status(make_args(order_id="bad-id", status="shipped"))
    assert exc_info.value.code == 1


def test_cmd_update_status_terminal_exits() -> None:
    resp = mock_response(409, {"detail": "Order is in a terminal state"})
    with patch("httpx.patch", return_value=resp):
        with pytest.raises(SystemExit) as exc_info:
            cli_main.cmd_update_status(make_args(order_id="o1", status="pending"))
    assert exc_info.value.code == 1


def test_cmd_update_status_invalid_status_exits() -> None:
    resp = mock_response(422, {"detail": "Invalid status"})
    with patch("httpx.patch", return_value=resp):
        with pytest.raises(SystemExit) as exc_info:
            cli_main.cmd_update_status(make_args(order_id="o1", status="badstatus"))
    assert exc_info.value.code == 1
