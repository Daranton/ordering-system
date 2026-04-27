# Architecture

This project has two separate interfaces over the same data model: a CLI and a FastAPI web API.

```
cli/main.py          →  direct access to domain layer
src/api/main.py      →  HTTP access via FastAPI

Both use:
src/utils/models.py  →  Order dataclass, OrderStatus enum, load/save
src/utils/ids.py     →  order ID generation
src/api/schemas.py   →  API input/output validation (API path only)
```

## Layers

### Domain layer — `src/utils/`

The core of the application. Has no knowledge of HTTP or CLI concerns.

- **`models.py`** - defines `Order` (the data structure), `OrderStatus` (the enum of valid states), and `load_orders`/`save_orders` (JSON persistence).
- **`ids.py`** - generates unique order IDs using `uuid4`.

### CLI layer - `cli/`

A command-line interface built with `argparse`. Reads and writes orders by calling the domain layer directly. Persists data to `data/orders.json`.

Commands: `create`, `list`, `get`.

### API layer - `src/api/`

A FastAPI web application. Currently has 4 placeholder endpoints and imports `schemas.py` for request/response validation. The API layer does not yet connect to the domain layer - wiring is future work.

- **`main.py`** — registers FastAPI routes.
- **`schemas.py`** — Pydantic models that validate incoming requests and shape outgoing responses.

## Data flow

### CLI path
```
user input (argparse)
    → cmd_create / cmd_list / cmd_get
    → load_orders (reads data/orders.json)
    → Order dataclass (domain logic + validation)
    → save_orders (writes data/orders.json)
```

### API path (future)
```
HTTP request (JSON)
    → Pydantic schema (OrderCreate / OrderUpdate)
    → Order dataclass
    → save_orders
    → Pydantic schema (OrderResponse)
    → HTTP response (JSON)
```
