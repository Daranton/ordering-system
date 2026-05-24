from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.order import Order, OrderItem, OrderStatus
from src.infrastructure.db.models import OrderItemModel, OrderModel


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, order: Order) -> Order:
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
        return _to_domain(db_order)

    def get(self, order_id: str) -> Order | None:
        db_order = self._session.get(OrderModel, order_id)
        if db_order is None or db_order.deleted_at is not None:
            return None
        return _to_domain(db_order)

    def list_by_status(self, status: OrderStatus | None) -> list[Order]:
        stmt = select(OrderModel).where(OrderModel.deleted_at.is_(None))
        if status is not None:
            stmt = stmt.where(OrderModel.status == status)
        return [_to_domain(o) for o in self._session.scalars(stmt).all()]

    def soft_delete(self, order_id: str) -> Order | None:
        db_order = self._session.get(OrderModel, order_id)
        if db_order is None or db_order.deleted_at is not None:
            return None
        db_order.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self._session.commit()
        self._session.refresh(db_order)
        return _to_domain(db_order)

    def update_status(self, order_id: str, status: OrderStatus) -> Order | None:
        db_order = self._session.get(OrderModel, order_id)
        if db_order is None:
            return None
        db_order.status = status
        self._session.commit()
        self._session.refresh(db_order)
        return _to_domain(db_order)


def _to_domain(db_order: OrderModel) -> Order:
    return Order(
        id=db_order.id,
        customer_name=db_order.customer_name,
        status=db_order.status,
        total=float(db_order.total),
        created_at=db_order.created_at,
        items=[
            OrderItem(
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
            )
            for item in db_order.items
        ],
    )
