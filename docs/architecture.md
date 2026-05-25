# Architecture

This project follows Domain-Driven Design (DDD) with four layers. Each layer has a single responsibility, and dependencies only point inward — outer layers import from inner layers, never the reverse. Nothing in `src/domain/` imports from any other layer in this project.

## Layer overview

```mermaid
flowchart TD
    CLI["cli/\n(argparse, HTTP client)"]

    subgraph api["src/api/"]
        MAIN["main.py\n← composition root"]
        SCHEMAS["schemas.py\n(Pydantic schemas)"]
    end

    APP["src/application/\n(OrderService)"]
    INFRA["src/infrastructure/\n(OrderRepository, SQLAlchemy)"]
    DOMAIN["src/domain/\n(Order, rules, exceptions, Protocol)"]

    CLI -->|HTTP| api
    MAIN -->|creates + calls| APP
    MAIN -->|creates| INFRA
    APP -->|depends on Protocol| DOMAIN
    INFRA -->|implements Protocol| DOMAIN
```

## Layers

### CLI — `cli/`

A command-line interface built with `argparse`. Talks to the API over HTTP — it does not access the domain or database directly.

### API — `src/api/`

The HTTP interface. Accepts requests, validates input, delegates to the service, and maps domain exceptions to HTTP status codes.

- **`main.py`** — FastAPI app, route handlers, and the composition root. The only file that imports from both `src/application/` and `src/infrastructure/` and wires them together.
- **`schemas.py`** — Pydantic models (`OrderCreate`, `OrderUpdate`, `OrderResponse`, `OrderItemSchema`) that validate HTTP input and shape HTTP output.

### Application — `src/application/`

Orchestrates domain objects and infrastructure. Has no HTTP or database knowledge of its own.

- **`services/order_service.py`** — `OrderService`: receives a repository via its constructor, calls domain methods, and raises domain exceptions. Also responsible for ID generation (`uuid4`) and timestamping (`datetime.now`).

### Infrastructure — `src/infrastructure/`

Implements the repository protocol using SQLAlchemy and PostgreSQL.

- **`db/models.py`** — `OrderModel`, `OrderItemModel`: SQLAlchemy ORM models that map to the `orders` and `order_items` tables.
- **`db/repositories/order_repository.py`** — `OrderRepository`: implements `OrderRepositoryProtocol`. Translates between domain objects and ORM models.
- **`db/connection.py`** — `SessionLocal`, `Base`: SQLAlchemy engine and session factory.

### Domain — `src/domain/`

The core of the application. Contains business rules and types only — no knowledge of HTTP, databases, or the CLI.

- **`order.py`** — `Order` aggregate, `OrderItem`, `OrderStatus` enum. `Order.transition_to()` enforces the terminal-state invariant.
- **`state_machine.py`** — `TERMINAL_STATUSES`: the set of statuses from which an order cannot transition.
- **`exceptions.py`** — `OrderNotFoundError`, `InvalidTransitionError`. Raised by the domain, caught by the API layer.
- **`repository.py`** — `OrderRepositoryProtocol`: a structural Protocol that defines what persistence operations the domain expects, without depending on any concrete implementation.

## Data flow

```mermaid
sequenceDiagram
    participant CLI as cli/
    participant API as src/api/main.py
    participant SVC as OrderService
    participant REPO as OrderRepository
    participant DB as PostgreSQL

    CLI->>API: HTTP request
    API->>SVC: call service method
    SVC->>REPO: call repository method
    REPO->>DB: SQL query
    DB-->>REPO: rows
    REPO-->>SVC: Order (domain object)
    SVC-->>API: Order / raises exception
    API-->>CLI: HTTP response (JSON)
```

## Dependency rule

`src/api/main.py` imports from both `src/application/` and `src/infrastructure/` as the composition root. `src/application/` imports only from `src/domain/` via the Protocol, never from `src/infrastructure/`. `src/domain/` has no outward arrows.

```mermaid
flowchart LR
    CLI -->|HTTP| MAIN["src/api/main.py"]
    MAIN -->|imports| APP["src/application/"]
    MAIN -->|imports| INFRA["src/infrastructure/"]
    APP -->|imports| DOMAIN["src/domain/"]
    INFRA -->|imports| DOMAIN
```
