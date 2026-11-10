# Ordering System

![CI](https://github.com/Daranton/ordering-system/actions/workflows/ci.yml/badge.svg)

A REST API and CLI tool for creating and managing orders.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

`.env` holds the database connection URL. The defaults in `.env.example` match the Docker Compose dev database — edit only if you're connecting to a different Postgres instance.

Run all commands from the project root.

## Database

Ensure `.env` is in place (see Setup), then start the development database:

```bash
docker compose up -d postgres
```

Apply migrations:

```bash
alembic upgrade head
```

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
| `DELETE` | `/orders/{id}` | Soft-delete an order |

### Status codes

- `201` — order created
- `204` — order deleted
- `404` — order not found
- `409` — order is in a terminal state (`cancelled` or `delivered`)
- `422` — request body failed validation

## Running the tests

Unit tests need no setup:

```bash
pytest tests/orders/unit
```

Integration tests run against a real Postgres. Start the test database first:

```bash
docker compose up -d postgres-test
pytest
```

Without the test database, integration tests are skipped with a hint (`pytest -rs` shows the reason). In CI they always run.

## Type checking

Strict mode is set in `pyproject.toml`:

```bash
mypy .
```

## CLI

The CLI communicates with the API over HTTP. Make sure the API is running before using it.

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

### Update an order's status

```bash
python -m cli.main update <order_id> <status>
```

Example:

```bash
python -m cli.main update 3f2a1b4c-8e9d-4f0a-b1c2-d3e4f5a6b7c8 shipped
```

## Valid statuses

`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`, `disputed`

## Project structure

Two bounded contexts, `orders` and `auth`, each with the same layered layout.

```
ordering-system/
├── src/
│   ├── orders/
│   │   ├── domain/                         # Pure business logic, no I/O
│   │   │   ├── order.py                    # Order, OrderItem, OrderStatus
│   │   │   ├── state_machine.py            # Allowed status transitions, terminal statuses
│   │   │   ├── exceptions.py               # OrderNotFoundError, InvalidTransitionError
│   │   │   └── repository.py               # OrderRepositoryProtocol (abstract interface)
│   │   ├── application/
│   │   │   └── services/
│   │   │       └── order_service.py        # Use cases, depends only on domain
│   │   ├── infrastructure/
│   │   │   └── db/
│   │   │       ├── connection.py           # SQLAlchemy engine and session
│   │   │       ├── models.py               # ORM models (OrderModel, OrderItemModel)
│   │   │       └── repositories/
│   │   │           └── order_repository.py # Concrete repository implementation
│   │   ├── api/
│   │   │   ├── main.py                     # FastAPI routes, dependency wiring
│   │   │   └── schemas.py                  # Pydantic request/response schemas
│   │   ├── alembic/                        # Orders migrations (alembic.ini)
│   │   └── config.py                       # DATABASE_URL from environment
│   └── auth/                               # Auth service scaffold, same layout
│       ├── domain/                         # User, UserRepositoryProtocol
│       ├── infrastructure/db/              # UserModel, UserRepository
│       ├── api/                            # FastAPI app with GET /health
│       ├── alembic/                        # Auth migrations (alembic-auth.ini)
│       └── config.py                       # AUTH_DATABASE_URL from environment
├── cli/
│   └── main.py                             # CLI client (communicates with API via HTTP)
└── tests/
    ├── conftest.py                         # Default DATABASE_URL for a fresh clone
    └── orders/
        ├── unit/                           # No database needed
        │   ├── test_order.py               # Order aggregate and status transitions
        │   ├── test_order_service.py       # Service layer (mocked repository)
        │   ├── test_schemas.py             # Pydantic schema validation
        │   └── test_cli.py                 # CLI client
        └── integration/                    # Real Postgres (postgres-test)
            ├── conftest.py                 # Engine, per-test transaction rollback, skip guard
            ├── test_order_repository.py    # Repository against the database
            └── test_orders.py              # Full stack through the API
```
