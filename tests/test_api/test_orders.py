import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.repository import OrderRepository, get_repository


VALID_PAYLOAD = {
    "customer_name": "Alice",
    "items": [{"product_name": "Widget", "quantity": 2, "unit_price": 9.99}],
}


@pytest.fixture
def client() -> TestClient:
    repo = OrderRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- Create ---

def test_create_order_success(client: TestClient) -> None:
    response = client.post("/orders", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Alice"
    assert data["status"] == "pending"
    assert data["total"] == pytest.approx(19.98)
    assert "id" in data


def test_create_order_missing_customer(client: TestClient) -> None:
    payload = {"items": [{"product_name": "Widget", "quantity": 1, "unit_price": 5.0}]}
    response = client.post("/orders", json=payload)
    assert response.status_code == 422


def test_create_order_empty_items(client: TestClient) -> None:
    payload = {"customer_name": "Alice", "items": []}
    response = client.post("/orders", json=payload)
    assert response.status_code == 422


def test_create_order_negative_quantity(client: TestClient) -> None:
    payload = {
        "customer_name": "Alice",
        "items": [{"product_name": "Widget", "quantity": -1, "unit_price": 5.0}],
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 422


# --- Get by ID ---

def test_get_order_by_id(client: TestClient) -> None:
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_get_order_not_found(client: TestClient) -> None:
    response = client.get("/orders/nonexistent-id")
    assert response.status_code == 404


# --- List ---

def test_list_orders_empty(client: TestClient) -> None:
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_list_orders_with_filter(client: TestClient) -> None:
    client.post("/orders", json=VALID_PAYLOAD)
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    client.patch(f"/orders/{order_id}", json={"status": "confirmed"})

    pending = client.get("/orders?status=pending").json()
    confirmed = client.get("/orders?status=confirmed").json()

    assert len(pending) == 1
    assert len(confirmed) == 1
    assert all(o["status"] == "pending" for o in pending)
    assert all(o["status"] == "confirmed" for o in confirmed)


# --- Patch ---

def test_patch_order_status(client: TestClient) -> None:
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    response = client.patch(f"/orders/{order_id}", json={"status": "confirmed"})
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_patch_terminal_order(client: TestClient) -> None:
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    client.patch(f"/orders/{order_id}", json={"status": "cancelled"})
    response = client.patch(f"/orders/{order_id}", json={"status": "confirmed"})
    assert response.status_code == 409


def test_patch_nonexistent_order(client: TestClient) -> None:
    response = client.patch("/orders/nonexistent-id", json={"status": "confirmed"})
    assert response.status_code == 404
