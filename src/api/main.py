import http
from datetime import datetime, timezone

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException

from src.api.repository import OrderRepository, get_repository
from src.api.schemas import OrderCreate, OrderResponse, OrderUpdate
from src.utils.ids import generate_order_id
from src.utils.models import OrderStatus

app = FastAPI(title = "Ordering System API",
              description = "API for managing orders in the ordering system",
              version = "1.0.0")

@app.get("/")
def root() -> dict[str, str]:
    return {"status": "Ordering System API is running!"}

@app.get("/hello/{name}")
def hello(name: str) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}

@app.get("/search")
def search(q: str = "", limit: int = 10) -> dict[str, str | int]:
    return {"q": q, "limit": limit}

@app.get("/status/{code}")
def get_status(code: int) -> dict[str, int | str]:
    try:
        phrase = http.HTTPStatus(code).phrase
    except ValueError:
        phrase = "Unknown status code"
    return {"code": code, "phrase": phrase}


@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(
    payload: OrderCreate,
    repo: OrderRepository = Depends(get_repository),
) -> OrderResponse:
    total = sum(item.quantity * item.unit_price for item in payload.items)
    order = OrderResponse(
        id=generate_order_id(),
        customer_name=payload.customer_name,
        items=payload.items,
        status=OrderStatus.PENDING,
        total=total,
        created_at=datetime.now(timezone.utc),
    )
    return repo.add(order)


@app.get("/orders", response_model=list[OrderResponse])
def list_orders(
    status: Optional[OrderStatus] = None,
    repo: OrderRepository = Depends(get_repository),
) -> list[OrderResponse]:
    orders = repo.list_all()
    if status is not None:
        orders = [o for o in orders if o.status == status]
    return orders


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    repo: OrderRepository = Depends(get_repository),
) -> OrderResponse:
    order = repo.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return order


TERMINAL_STATUSES = {OrderStatus.CANCELLED, OrderStatus.DELIVERED}

@app.patch("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    payload: OrderUpdate,
    repo: OrderRepository = Depends(get_repository),
) -> OrderResponse:
    order = repo.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    if order.status in TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail=f"Order '{order_id}' is in a terminal state ({order.status}) and cannot be updated")
    updated = order.model_copy(update={"status": payload.status})
    return repo.update(updated)

