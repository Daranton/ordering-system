import http
from collections.abc import Generator
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.infrastructure.db.connection import SessionLocal
from src.api.schemas import OrderCreate, OrderItemSchema, OrderResponse, OrderUpdate
from src.infrastructure.db.repositories.order_repository import OrderRepository
from src.domain.repository import OrderRepositoryProtocol
from src.application.services.order_service import OrderService
from src.domain.exceptions import InvalidTransitionError, OrderNotFoundError
from src.domain.order import Order, OrderItem, OrderStatus


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)

# route function -> Depends(get_service) -> Depends(get_repository) -> Depends(get_db) -> SessionLocal()
def get_service(repo: OrderRepositoryProtocol = Depends(get_repository)) -> OrderService:
    return OrderService(repo)


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=[
            OrderItemSchema(
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ],
    )


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
    items = [
        OrderItem(
            product_name=i.product_name,
            quantity=i.quantity,
            unit_price=i.unit_price,
        )
        for i in payload.items
    ]
    return _to_response(svc.create_order(payload.customer_name, items))


@app.get("/orders", response_model=list[OrderResponse])
def list_orders(
    status: Optional[OrderStatus] = None,
    svc: OrderService = Depends(get_service),
) -> list[OrderResponse]:
    return [_to_response(o) for o in svc.list_orders(status)]


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    svc: OrderService = Depends(get_service),
) -> OrderResponse:
    order = svc.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return _to_response(order)


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
    if payload.status is None:
        order = svc.get_order(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
        return _to_response(order)
    try:
        result = svc.update_order_status(order_id, payload.status)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    except InvalidTransitionError as e:
        raise HTTPException(status_code=409, detail=f"Order '{order_id}' is in a terminal state ({e.current_status}) and cannot be updated")
    return _to_response(result)
