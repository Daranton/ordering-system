from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db_models import OrderItemModel, OrderModel
from src.api.schemas import OrderItemSchema, OrderResponse
from src.utils.models import OrderStatus


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, order: OrderResponse) -> OrderResponse:
        db_order = OrderModel(
            id=order.id,
            customer_name=order.customer_name,
            status=order.status,
            total=order.total,
            created_at=order.created_at,
            items=[
                OrderItemModel(
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in order.items
            ],
        )
        self._session.add(db_order)
        self._session.commit()
        self._session.refresh(db_order)
        return _to_response(db_order)

    def get(self, order_id: str) -> OrderResponse | None:
        db_order = self._session.get(OrderModel, order_id)
        return _to_response(db_order) if db_order else None

    def list_by_status(self, status: OrderStatus | None) -> list[OrderResponse]:
        stmt = select(OrderModel)
        if status is not None:
            stmt = stmt.where(OrderModel.status == status)
        return [_to_response(o) for o in self._session.scalars(stmt).all()]

    def update_status(self, order_id: str, status: OrderStatus) -> OrderResponse | None:
        db_order = self._session.get(OrderModel, order_id)
        if db_order is None:
            return None
        db_order.status = status
        self._session.commit()
        self._session.refresh(db_order)
        return _to_response(db_order)


def _to_response(db_order: OrderModel) -> OrderResponse:
    return OrderResponse(
        id=db_order.id,
        customer_name=db_order.customer_name,
        status=db_order.status,
        total=float(db_order.total),
        created_at=db_order.created_at,
        items=[
            OrderItemSchema(
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
            )
            for item in db_order.items
        ],
    )
