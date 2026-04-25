import pytest
from src.utils.validation import validate_status


@pytest.mark.parametrize("status", ["pending", "confirmed", "shipped", "delivered", "cancelled", "disputed"])
def test_all_valid_statuses(status: str) -> None:
    assert validate_status(status) is True


def test_valid_status_uppercase() -> None:
    assert validate_status("PENDING") is True


def test_valid_status_mixed_case() -> None:
    assert validate_status("ShiPpeD") is True


def test_invalid_status() -> None:
    assert validate_status("unknown") is False


def test_empty_string() -> None:
    assert validate_status("") is False
