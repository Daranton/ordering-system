# Week 2: FastAPI Fundamentals & First Endpoint

**Goal:** Take the `Order` dataclass, enum, and validation helpers from Week 1 and expose them through a real REST API. By Friday you have a working FastAPI service with full CRUD endpoints for orders, validated with Pydantic, fully covered by tests. Persistence is still in-memory — Postgres arrives in Week 3.

**Why this matters:** This is the week Python becomes a web service. Everything you build now (Pydantic models, dependency injection, error handling, testing) is the foundation every other service in the system will reuse. The Auth, Users, Orders, and Payments services in later weeks all follow this same shape.

**Carrying forward from Week 1:**
- The `Order` dataclass becomes a set of Pydantic models
- The `OrderStatus` enum is reused as-is (Pydantic handles enums natively)
- The validation helpers from `utils/validation.py` become Pydantic field validators
- The CLI from Week 1 still works against the JSON file — keep it as a useful tool
- The project structure expands: a new `api/` package sits alongside `cli/`

---

## Pre-Week Setup

Activate the virtual environment from Week 1 and install this week's dependencies:

```bash
source .venv/bin/activate
pip install fastapi 'uvicorn[standard]' pytest httpx
pip freeze > requirements.txt
```

**What each does:**
- `fastapi` — the web framework
- `uvicorn[standard]` — the ASGI server that runs FastAPI; `[standard]` adds useful extras like auto-reload
- `pytest` — the testing framework
- `httpx` — the HTTP client FastAPI's `TestClient` uses under the hood

Quick sanity check:

```bash
python -c "import fastapi, pytest, httpx; print('OK')"
```

---

## Monday — HTTP Fundamentals & FastAPI Hello World

**Goal:** Understand what HTTP actually is and get a minimal FastAPI app running.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| HTTP overview: requests, responses, methods | [MDN — An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview) | 30 min |
| HTTP methods (GET, POST, PUT, PATCH, DELETE) | [MDN — HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods) | 20 min |
| HTTP status codes — focus on 2xx, 4xx, 5xx | [MDN — HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) | 30 min |
| FastAPI introduction & first steps | [FastAPI Tutorial — First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) | 30 min |
| Path parameters | [FastAPI Tutorial — Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/) | 30 min |
| Query parameters | [FastAPI Tutorial — Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) | 30 min |

### Activities

1. Create a new package `src/api/` with an `__init__.py` and `main.py`
2. Write a minimal FastAPI app:

   ```python
   from fastapi import FastAPI

   app = FastAPI(title="Ordering System API")

   @app.get("/")
   def root() -> dict[str, str]:
       return {"status": "ok"}
   ```

3. Run it: `uvicorn src.api.main:app --reload`
4. Visit `http://localhost:8000` and `http://localhost:8000/docs` — explore the auto-generated Swagger UI
5. Add three more endpoints to practice path and query parameters:
   - `GET /hello/{name}` — returns a greeting
   - `GET /search?q=widget&limit=10` — echoes back the query params
   - `GET /status/{code}` — returns the matching HTTP status (use `from fastapi import status`)

### End of day checkpoint

You can run a FastAPI app, you understand the difference between path and query parameters, and you've explored `/docs` to see how FastAPI generates documentation automatically.

---

## Tuesday — Pydantic Models & Migrating the Order Dataclass

**Goal:** Convert Week 1's `Order` dataclass into Pydantic models. Understand why APIs need separate models for input, output, and updates.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| Why Pydantic exists, models vs dataclasses | [Pydantic — Why use Pydantic](https://docs.pydantic.dev/latest/why/) | 20 min |
| Pydantic models — the basics | [Pydantic — Models](https://docs.pydantic.dev/latest/concepts/models/) | 45 min |
| Field validation and constraints | [Pydantic — Fields](https://docs.pydantic.dev/latest/concepts/fields/) | 30 min |
| Validators (`@field_validator`, `@model_validator`) | [Pydantic — Validators](https://docs.pydantic.dev/latest/concepts/validators/) | 30 min |
| FastAPI request body with Pydantic | [FastAPI Tutorial — Request Body](https://fastapi.tiangolo.com/tutorial/body/) | 30 min |
| Response models | [FastAPI Tutorial — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/) | 30 min |

### Conceptual point worth understanding

In a real API, the same "thing" looks different at different points in its lifecycle:

- **OrderCreate** — what the client sends to create an order. No `id`, no `created_at`, no `status` (server assigns these).
- **Order** — the full domain object as stored. Has everything.
- **OrderUpdate** — what the client sends to modify an order. All fields optional.
- **OrderResponse** — what the API returns. Often identical to `Order`, but sometimes hides internal fields.

This separation is one of the most important habits to build. Don't shortcut it.

### Activities

1. Create `src/api/schemas.py` with Pydantic models:

   ```python
   from datetime import datetime
   from pydantic import BaseModel, Field, field_validator
   from src.utils.models import OrderStatus  # reuse Week 1's enum

   class OrderItemSchema(BaseModel):
       product_name: str = Field(min_length=1, max_length=200)
       quantity: int = Field(gt=0)
       unit_price: float = Field(gt=0)

   class OrderCreate(BaseModel):
       customer_name: str = Field(min_length=1, max_length=100)
       items: list[OrderItemSchema] = Field(min_length=1)

   class OrderUpdate(BaseModel):
       status: OrderStatus | None = None

   class OrderResponse(BaseModel):
       id: str
       customer_name: str
       items: list[OrderItemSchema]
       status: OrderStatus
       total: float
       created_at: datetime
   ```

2. Move logic from Week 1's validation helpers into Pydantic field validators where appropriate. For example, if you had a function that checked `customer_name` wasn't empty, that's now `Field(min_length=1)`.

3. Write a small script or REPL session that constructs valid and invalid `OrderCreate` instances. Observe the validation errors Pydantic produces — they're rich and structured.

4. Run `mypy --strict` on the new code. Pydantic v2 has excellent type support — there should be no errors.

### End of day checkpoint

You have Pydantic models for create/update/response. You understand why they're separate. You've seen Pydantic validation errors and they make sense to you.

---

## Wednesday — Build the Core Endpoints (POST, GET, GET by ID)

**Goal:** Wire the Pydantic models into real endpoints backed by an in-memory store. Establish the repository pattern so swapping for Postgres in Week 3 is a clean change.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| FastAPI dependency injection | [FastAPI Tutorial — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) | 45 min |
| Handling errors with `HTTPException` | [FastAPI Tutorial — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) | 30 min |
| Status codes in FastAPI | [FastAPI Tutorial — Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/) | 15 min |
| Repository pattern — overview | [Martin Fowler — Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) | 15 min |

### The repository pattern (key concept)

Instead of hard-coding `dict` access into your endpoints, wrap storage behind an interface. The endpoint doesn't know if it's talking to a dict, a JSON file, or Postgres — it just calls `repo.get(order_id)`. When Week 3 arrives, you swap the implementation, not the endpoints.

### Activities

1. Create `src/api/repository.py`:

   ```python
   from src.utils.models import Order  # reuse Week 1's domain model

   class OrderRepository:
       def __init__(self) -> None:
           self._orders: dict[str, Order] = {}

       def add(self, order: Order) -> Order:
           self._orders[order.id] = order
           return order

       def get(self, order_id: str) -> Order | None:
           return self._orders.get(order_id)

       def list_all(self) -> list[Order]:
           return list(self._orders.values())
   ```

2. Create a dependency that provides the repository (singleton pattern via FastAPI):

   ```python
   from functools import lru_cache

   @lru_cache
   def get_repository() -> OrderRepository:
       return OrderRepository()
   ```

3. Build the endpoints in `src/api/main.py`:
   - `POST /orders` — accepts `OrderCreate`, creates an `Order` (use Week 1's `generate_order_id`), calculates total, sets status to `PENDING`, stores it, returns `OrderResponse` with status `201`
   - `GET /orders` — returns `list[OrderResponse]`
   - `GET /orders/{order_id}` — returns the order or raises `HTTPException(404)`

4. Test by hand using `/docs` — create an order, list it, fetch it by ID, fetch a non-existent ID and confirm you get a clean 404.

### End of day checkpoint

Three endpoints work end-to-end. The repository sits behind a dependency. The CLI from Week 1 still works (it uses the JSON file independently). Both can coexist.

---

## Thursday — PATCH, Filtering, and the State Machine Foundation

**Goal:** Add the update endpoint with state-aware logic, plus query filtering. Start enforcing the order state machine — this becomes critical in Week 6.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| Path operation configuration | [FastAPI Tutorial — Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/) | 20 min |
| Body — Updates (PUT vs PATCH) | [FastAPI Tutorial — Body Updates](https://fastapi.tiangolo.com/tutorial/body-updates/) | 30 min |
| Query parameters with Pydantic models | [FastAPI Tutorial — Query Param Models](https://fastapi.tiangolo.com/tutorial/query-param-models/) | 20 min |
| State machines (conceptual) | [Wikipedia — Finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) (read intro and "Concepts and terminology") | 20 min |

### The state machine — start simple

The full state machine arrives in Week 6 with proper transition guards. For now, just enforce one rule: you can transition between any two statuses, but `CANCELLED` and `DELIVERED` are terminal — once an order is in either state, it cannot change.

This builds the habit of thinking about transitions instead of just "set the field to whatever the client sent".

### Activities

1. Add `PATCH /orders/{order_id}` to update an order's status:
   - Accept `OrderUpdate`
   - If the order is in a terminal state (`CANCELLED` or `DELIVERED`), raise `HTTPException(409)` — Conflict
   - Otherwise update the status and return the updated `OrderResponse`

2. Add a filtering query parameter to `GET /orders`:
   - `GET /orders?status=PENDING` — only returns orders with that status
   - `GET /orders` (no filter) — returns all
   - Pass the status as an `Optional[OrderStatus]` query param so FastAPI validates it automatically

3. Add the repository method to support filtering:

   ```python
   def list_by_status(self, status: OrderStatus | None) -> list[Order]:
       if status is None:
           return self.list_all()
       return [o for o in self._orders.values() if o.status == status]
   ```

4. Add proper response status codes to every endpoint:
   - `POST /orders` → `201 Created`
   - `GET` endpoints → `200 OK`
   - `PATCH /orders/{id}` → `200 OK` on success, `404` not found, `409` terminal state

5. Test by hand via `/docs`:
   - Create an order
   - Patch it to `CONFIRMED` → success
   - Patch it to `CANCELLED` → success
   - Patch it again to anything → 409
   - List orders filtered by `CANCELLED` → see your order

### End of day checkpoint

All four endpoints work. State transitions are guarded for terminal states. Filtering works. The auto-generated `/docs` UI shows everything cleanly with proper status codes.

---

## Friday — Testing with Pytest & Final Polish

**Goal:** Cover everything with automated tests. From this week onward, untested code is broken code.

### What to read

| Topic | Source | Time |
|-------|--------|------|
| Pytest — getting started | [Pytest — Get Started](https://docs.pytest.org/en/stable/getting-started.html) | 30 min |
| Pytest fixtures | [Pytest — How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) | 45 min |
| FastAPI testing | [FastAPI Tutorial — Testing](https://fastapi.tiangolo.com/tutorial/testing/) | 30 min |
| Overriding dependencies in tests | [FastAPI Advanced — Testing Dependencies with Overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/) | 20 min |

### The dependency override pattern (key for this week)

In production, `get_repository()` returns the singleton. In tests, you want a fresh repository per test so they don't pollute each other. FastAPI's `app.dependency_overrides` lets you swap the dependency cleanly:

```python
@pytest.fixture
def client():
    app.dependency_overrides[get_repository] = lambda: OrderRepository()
    yield TestClient(app)
    app.dependency_overrides.clear()
```

This is the same pattern you'll use later to swap the real Postgres repository for a test one.

### Activities

1. Create `tests/test_api/test_orders.py` with tests for:
   - **Create:**
     - `test_create_order_success` — valid payload returns 201 and the created order
     - `test_create_order_missing_customer` — returns 422
     - `test_create_order_empty_items` — returns 422
     - `test_create_order_negative_quantity` — returns 422
   - **Get:**
     - `test_get_order_by_id` — returns 200 and the order
     - `test_get_order_not_found` — returns 404
   - **List:**
     - `test_list_orders_empty` — returns empty list
     - `test_list_orders_with_filter` — only returns matching status
   - **Patch:**
     - `test_patch_order_status` — successfully transitions
     - `test_patch_terminal_order` — returns 409
     - `test_patch_nonexistent_order` — returns 404

2. Use a fixture to provide a fresh `TestClient` per test.

3. Run the full test suite: `pytest -v`. All tests should pass.

4. **Quality pass:**
   - Run `mypy --strict` on the entire codebase — fix any issues
   - Update the project `README.md`:
     - How to install dependencies
     - How to run the API (`uvicorn` command)
     - How to run the tests (`pytest`)
     - List the endpoints
   - Commit and push to GitHub

### End of day checkpoint

10+ tests passing. `mypy --strict` is clean. The README explains how to run and test the service. The repo is portfolio-ready for Week 2.

---

## Week 2 Deliverable Checklist

- [ ] FastAPI app runs via `uvicorn src.api.main:app --reload`
- [ ] Pydantic models for create, update, response — all separate
- [ ] `OrderStatus` enum from Week 1 reused without modification
- [ ] Repository pattern wraps the in-memory dict, exposed via dependency injection
- [ ] Endpoints: `POST /orders`, `GET /orders`, `GET /orders/{id}`, `PATCH /orders/{id}`
- [ ] Status filtering via `GET /orders?status=PENDING`
- [ ] Terminal state guard: `CANCELLED` and `DELIVERED` orders cannot be modified
- [ ] Proper HTTP status codes: 201 for create, 404 for not found, 409 for state conflicts, 422 for validation
- [ ] 10+ pytest tests, all passing, using `TestClient` with dependency overrides
- [ ] `mypy --strict` passes with zero errors
- [ ] `README.md` updated with run and test instructions
- [ ] CLI from Week 1 still works (it operates on the JSON file independently)

---

## Recommended Reading Order (Full Week)

1. [MDN — HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview) — understand the protocol before the framework
2. [FastAPI Tutorial — First Steps through Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/) — sequential, work top-to-bottom
3. [Pydantic — Models, Fields, Validators](https://docs.pydantic.dev/latest/concepts/models/) — deep on Pydantic since you'll use it everywhere
4. [FastAPI Tutorial — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) — the killer feature for clean architecture
5. [Pytest — Get Started, Fixtures](https://docs.pytest.org/en/stable/) — testing is your safety net
6. [FastAPI Tutorial — Testing & Testing Dependencies](https://fastapi.tiangolo.com/tutorial/testing/) — wires it all together
7. [Martin Fowler — Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) — the architectural idea behind the abstraction

---

## Looking Ahead

Next week the in-memory dict goes away. The `OrderRepository` interface stays exactly the same, but its implementation switches to SQLAlchemy talking to a real Postgres instance running in Docker. Because the repository is dependency-injected and the endpoints don't know how it's implemented, the change touches `repository.py` and config, but not the endpoints or the tests (much). That's the payoff of building it this way from the start.