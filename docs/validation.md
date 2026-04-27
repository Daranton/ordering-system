# Validation

Validation is split across two layers depending on which interface is being used.

## Domain layer (`models.py`)

The `Order` dataclass validates itself in `__post_init__`. This runs regardless of whether the order came from the CLI or the API.

- `quantity` must not be negative — raises `ValueError` if it is
- `status` is coerced from a string to `OrderStatus` if needed

This is the last line of defence. Even if validation higher up the stack is bypassed or skipped, an `Order` object cannot be created in an invalid state.

## API layer (`schemas.py`)

Pydantic validates incoming HTTP request data before it reaches domain code.

### OrderItemSchema
- `product_name` - non-empty string, max 200 characters
- `quantity` - integer greater than 0
- `unit_price` - float greater than 0

### OrderCreate
- `customer_name` - non-empty string, max 100 characters
- `items` - list with at least one `OrderItemSchema`

### OrderUpdate
- `status` - optional; if provided, normalised to lowercase then checked against `OrderStatus`

The `normalise_status` field validator runs with `mode="before"`, meaning it transforms the raw input string before Pydantic attempts enum coercion. This is what allows `"PENDING"` and `"ShiPpeD"` to be accepted.

## Why both layers?

The CLI bypasses the API schemas entirely - it reads `argparse` input and constructs `Order` objects directly. If validation only existed in `schemas.py`, the CLI would have no protection. The domain layer validation in `models.py` ensures both interfaces enforce the same rules.

```
CLI input  →  models.py validation  ✓
API input  →  schemas.py validation  →  models.py validation  ✓
```
