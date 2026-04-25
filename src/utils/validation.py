from src.utils.models import OrderStatus


def validate_status(status: str) -> bool:
    """Return True if status is a recognised order status."""
    try:
        OrderStatus(status.lower())
        return True
    except ValueError:
        return False
