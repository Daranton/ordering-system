from pydantic import ValidationError
from src.api.schemas import OrderCreate

cases: list[tuple[str, dict[str, object]]] = [
    ("valid order", {
        "customer_name": "Alice",
        "items": [{"product_name": "Widget", "quantity": 2, "unit_price": 9.99}],
    }),
    ("empty customer name", {
        "customer_name": "",
        "items": [{"product_name": "Widget", "quantity": 2, "unit_price": 9.99}],
    }),
    ("no items", {
        "customer_name": "Alice",
        "items": [],
    }),
    ("negative quantity", {
        "customer_name": "Alice",
        "items": [{"product_name": "Widget", "quantity": -1, "unit_price": 9.99}],
    }),
    ("zero unit price", {
        "customer_name": "Alice",
        "items": [{"product_name": "Widget", "quantity": 1, "unit_price": 0}],
    }),
    ("missing fields", {
        "customer_name": "Alice",
        "items": [{"quantity": 1}],
    }),
    ("multiple errors", {
        "customer_name": "",
        "items": [{"product_name": "", "quantity": -1, "unit_price": 0}],
    }),
]

for label, data in cases:
    print(f"--- {label} ---")
    try:
        order = OrderCreate.model_validate(data)
        print(f"OK: customer={order.customer_name!r}, items={len(order.items)}")
    except ValidationError as e:
        for error in e.errors():
            loc = " -> ".join(str(p) for p in error["loc"])
            print(f"  field: {loc}")
            print(f"  error: {error['msg']}")
            print(f"  type:  {error['type']}")
    print()
