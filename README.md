# Ordering System

A REST API and CLI tool for creating and managing orders.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run all commands from the project root.

## Running the API

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs (Swagger UI) at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/orders` | Create a new order |
| `GET` | `/orders` | List all orders (optional `?status=` filter) |
| `GET` | `/orders/{id}` | Get a single order by ID |
| `PATCH` | `/orders/{id}` | Update an order's status |

### Status codes

- `201` — order created
- `404` — order not found
- `409` — order is in a terminal state (`cancelled` or `delivered`)
- `422` — request body failed validation

## Running the tests

```bash
pytest
```

## Type checking

```bash
mypy --strict .
```

## CLI

The CLI operates on a local JSON file independently of the API.

### Create an order

```bash
python -m cli.main create --customer "Alice" --item "Widget" --quantity 3
```

### List all orders

```bash
python -m cli.main list
python -m cli.main list --status shipped
```

### Get a single order

```bash
python -m cli.main get 3f2a1b4c-8e9d-4f0a-b1c2-d3e4f5a6b7c8
```

## Valid statuses

`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`, `disputed`

## Project structure

```
ordering-system/
├── src/
│   ├── api/
│   │   ├── main.py          # FastAPI app and endpoints
│   │   ├── repository.py    # In-memory order storage
│   │   └── schemas.py       # Pydantic models (OrderCreate, OrderUpdate, OrderResponse)
│   └── utils/
│       ├── models.py        # Order dataclass, OrderStatus enum, load/save helpers
│       ├── ids.py           # UUID generation
│       └── validation.py    # Status validation
├── cli/main.py              # CLI entry point (argparse)
├── data/orders.json         # CLI persisted orders
└── tests/
    ├── test_api/
    │   └── test_orders.py   # API endpoint tests
    ├── test_models.py        # Order dataclass and JSON persistence
    ├── test_ids.py           # ID generation
    ├── test_cli.py           # CLI command functions
    └── test_schemas.py       # Pydantic schema validation
```
