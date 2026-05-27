import pytest
from pydantic import ValidationError
from src.api.schemas import OrderCreate, OrderUpdate


@pytest.mark.parametrize("status", ["pending", "confirmed", "shipped", "delivered", "cancelled", "disputed"])
def test_valid_status(status: str) -> None:
    result = OrderUpdate.model_validate({"status": status}).status
    assert result is not None
    assert result.value == status


def test_valid_status_uppercase() -> None:
    result = OrderUpdate.model_validate({"status": "PENDING"}).status
    assert result is not None
    assert result.value == "pending"


def test_valid_status_mixed_case() -> None:
    result = OrderUpdate.model_validate({"status": "ShiPpeD"}).status
    assert result is not None
    assert result.value == "shipped"


def test_invalid_status_raises() -> None:
    with pytest.raises(ValidationError):
        OrderUpdate.model_validate({"status": "unknown"})


def test_empty_status_raises() -> None:
    with pytest.raises(ValidationError):
        OrderUpdate.model_validate({"status": ""})


def test_none_status_is_accepted() -> None:
    assert OrderUpdate.model_validate({"status": None}).status is None


# --- OrderCreate ---

VALID_ITEM = {"product_name": "Widget", "quantity": 2, "unit_price": 9.99}


def test_order_create_valid() -> None:
    result = OrderCreate.model_validate({"customer_name": "Alice", "items": [VALID_ITEM]})
    assert result.customer_name == "Alice"
    assert len(result.items) == 1


def test_order_create_empty_customer_raises() -> None:
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({"customer_name": "", "items": [VALID_ITEM]})


def test_order_create_empty_items_raises() -> None:
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({"customer_name": "Alice", "items": []})


# --- OrderItemSchema ---

def test_order_item_zero_quantity_raises() -> None:
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({"customer_name": "Alice", "items": [
            {"product_name": "Widget", "quantity": 0, "unit_price": 9.99}
        ]})


def test_order_item_negative_quantity_raises() -> None:
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({"customer_name": "Alice", "items": [
            {"product_name": "Widget", "quantity": -1, "unit_price": 9.99}
        ]})


def test_order_item_zero_unit_price_raises() -> None:
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({"customer_name": "Alice", "items": [
            {"product_name": "Widget", "quantity": 1, "unit_price": 0}
        ]})


def test_order_item_negative_unit_price_raises() -> None:
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({"customer_name": "Alice", "items": [
            {"product_name": "Widget", "quantity": 1, "unit_price": -5.0}
        ]})


def test_order_item_empty_product_name_raises() -> None:
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({"customer_name": "Alice", "items": [
            {"product_name": "", "quantity": 1, "unit_price": 9.99}
        ]})
