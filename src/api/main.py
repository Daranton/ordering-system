import http
from collections.abc import Generator
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.api.database import SessionLocal
from src.api.schemas import OrderCreate, OrderResponse, OrderUpdate
from src.repository.order_repository import OrderRepository
from src.service.order_service import OrderService, _NotFound, _Terminal
from src.utils.models import OrderStatus


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)

# route function -> Depends(get_service) -> Depends(get_repository) -> Depends(get_db) -> SessionLocal()
def get_service(repo: OrderRepository = Depends(get_repository)) -> OrderService:
    return OrderService(repo)


app = FastAPI(title="Ordering System API",
              description="API for managing orders in the ordering system",
              version="1.0.0")


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
    svc: OrderService = Depends(get_service),
) -> OrderResponse:
    return svc.create_order(payload)


@app.get("/orders", response_model=list[OrderResponse])
def list_orders(
    status: Optional[OrderStatus] = None,
    svc: OrderService = Depends(get_service),
) -> list[OrderResponse]:
    return svc.list_orders(status)


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    svc: OrderService = Depends(get_service),
) -> OrderResponse:
    order = svc.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return order


@app.delete("/orders/{order_id}", status_code=204)
def delete_order(
    order_id: str,
    svc: OrderService = Depends(get_service),
) -> None:
    if not svc.delete_order(order_id):
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


@app.patch("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    payload: OrderUpdate,
    svc: OrderService = Depends(get_service),
) -> OrderResponse:
    result = svc.update_order_status(order_id, payload)
    if isinstance(result, _NotFound):
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    if isinstance(result, _Terminal):
        raise HTTPException(status_code=409, detail=f"Order '{order_id}' is in a terminal state ({result.status}) and cannot be updated")
    return result
