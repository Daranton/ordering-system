import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VALID_STATUSES: set[str] = {"pending", "confirmed", "shipped", "delivered", "cancelled", "disputed"}


@dataclass
class Order:
    order_id: str
    customer: str
    item: str
    quantity: int
    status: str = field(default="pending")
    amount: float = 0.0

    def __post_init__(self) -> None:
        if self.quantity < 0:
            raise ValueError(f"quantity cannot be negative, got {self.quantity}")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"invalid status '{self.status}', must be one of {VALID_STATUSES}")

    def update_status(self, new_status: str) -> None:
        if new_status not in VALID_STATUSES:
            raise ValueError(f"invalid status '{new_status}', must be one of {VALID_STATUSES}")
        self.status = new_status

    def __repr__(self) -> str:
        return (
            f"Order({self.order_id!r}, customer={self.customer!r}, item={self.item!r}, "
            f"qty={self.quantity}, amount={self.amount}, status={self.status!r})"
        )


def load_orders(filepath: Path) -> dict[str, "Order"]:
    """Read orders from a JSON file. Returns empty dict on missing file or bad JSON."""
    try:
        with open(filepath, "r") as f:
            data: Any = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"expected JSON object, got {type(data).__name__}")
        return {oid: Order(order_id=oid, **od) for oid, od in data.items()}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Warning: could not parse {filepath}: {e}")
        return {}


def save_orders(filepath: Path, orders: dict[str, "Order"]) -> None:
    """Write orders dict to a JSON file, creating parent directories if needed."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = {
        oid: {
            "customer": o.customer,
            "item": o.item,
            "quantity": o.quantity,
            "status": o.status,
            "amount": o.amount,
        }
        for oid, o in orders.items()
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
