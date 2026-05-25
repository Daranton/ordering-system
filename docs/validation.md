# Validation

Validation is split across two layers: the API layer catches bad input at the HTTP boundary, and the domain layer enforces business invariants regardless of how the domain is called.

## API layer (`src/api/schemas.py`)

Pydantic validates all incoming HTTP request data before it reaches domain code.

### OrderItemSchema
- `product_name` — non-empty string, max 200 characters
- `quantity` — integer greater than 0
- `unit_price` — float greater than 0

### OrderCreate
- `customer_name` — non-empty string, max 100 characters
- `items` — list with at least one `OrderItemSchema`

### OrderUpdate
- `status` — optional; if provided, normalised to lowercase then checked against `OrderStatus`

The `normalise_status` field validator runs with `mode="before"`, meaning it transforms the raw input string before Pydantic attempts enum coercion. This is what allows `"PENDING"` and `"ShiPpeD"` to be accepted.

## Domain layer (`src/domain/`)

The domain enforces business invariants that Pydantic cannot express — specifically, rules about state transitions.

### `Order.transition_to(new_status)`

Defined in `src/domain/order.py`. Called by `OrderService` whenever an order's status is updated.

- If the current status is in `TERMINAL_STATUSES` (`CANCELLED` or `DELIVERED`), raises `InvalidTransitionError`.
- Otherwise, updates `self.status` to `new_status`.

`InvalidTransitionError` is defined in `src/domain/exceptions.py` and carries the current status as `current_status`. The API layer catches it and returns a `409 Conflict` response.

## Why both layers?

The two layers guard against different threats:

- **Pydantic** guards against invalid external input — malformed JSON, wrong types, out-of-range values. It runs at the HTTP boundary and rejects bad requests before they reach the domain.
- **Domain validation** guards against misuse from within the codebase — a service or future caller attempting an illegal state transition regardless of where the request came from.

```
HTTP request  →  schemas.py (Pydantic)  →  OrderService  →  Order.transition_to()
                      ↓ rejects bad input          ↓ raises InvalidTransitionError
                   422 Unprocessable             409 Conflict
```
