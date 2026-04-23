# connected to main.py 
# "from src.utils.ids import generate_order_id"

import uuid


def generate_order_id() -> str:
    """Return a new unique order ID."""
    return str(uuid.uuid4())
