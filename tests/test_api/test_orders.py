import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


VALID_PAYLOAD = {
    "customer_name": "Alice",
    "items": [{"product_name": "Widget", "quantity": 2, "unit_price": 9.99}],
}


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


# --- Persistence ---

def test_order_persists_across_requests(client: TestClient) -> None:
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id
    assert response.json()["customer_name"] == "Alice"


def test_order_items_are_stored(client: TestClient) -> None:
    payload = {
        "customer_name": "Bob",
        "items": [
            {"product_name": "Widget", "quantity": 2, "unit_price": 9.99},
            {"product_name": "Gadget", "quantity": 1, "unit_price": 24.99},
        ],
    }
    order_id = client.post("/orders", json=payload).json()["id"]
    data = client.get(f"/orders/{order_id}").json()
    assert len(data["items"]) == 2
    product_names = {item["product_name"] for item in data["items"]}
    assert product_names == {"Widget", "Gadget"}
    assert data["total"] == pytest.approx(44.97)


# --- Soft delete ---

def test_delete_order_soft_deletes(client: TestClient) -> None:
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    assert client.delete(f"/orders/{order_id}").status_code == 204
    assert client.get(f"/orders/{order_id}").status_code == 404


def test_deleted_order_excluded_from_list(client: TestClient) -> None:
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    client.delete(f"/orders/{order_id}")
    orders = client.get("/orders").json()
    assert all(o["id"] != order_id for o in orders)


def test_deleted_order_still_in_database(client: TestClient, db_session: Session) -> None:
    from src.api.db_models import OrderModel
    order_id = client.post("/orders", json=VALID_PAYLOAD).json()["id"]
    client.delete(f"/orders/{order_id}")
    db_order = db_session.get(OrderModel, order_id)
    assert db_order is not None
    assert db_order.deleted_at is not None


def test_delete_order_not_found(client: TestClient) -> None:
    assert client.delete("/orders/nonexistent-id").status_code == 404
