from utils.models import VALID_STATUSES


def validate_status(status: str) -> bool:
    """Return True if status is a recognised order status."""
    return status.lower() in VALID_STATUSES
