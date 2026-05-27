import pytest
from pydantic import ValidationError
from src.api.schemas import OrderUpdate


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
