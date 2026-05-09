from sqlalchemy import select

from src.api.database import Base, SessionLocal, engine
from src.api.db_models import OrderItemModel, OrderModel
from src.utils.models import OrderStatus
from datetime import datetime, timezone

# Create tables (Alembic takes over from Wednesday)
Base.metadata.create_all(engine)

# --- Insert ---
with SessionLocal() as session:
    order = OrderModel(
        id="ord-001",
        customer_name="Alice",
        status=OrderStatus.PENDING,
        total=27.50,
        created_at=datetime.now(timezone.utc),
        items=[
            OrderItemModel(product_name="Burger", quantity=2, unit_price=9.00),
            OrderItemModel(product_name="Fries", quantity=1, unit_price=4.50),
            OrderItemModel(product_name="Soda", quantity=1, unit_price=5.00),
        ],
    )
    session.add(order)
    session.commit()
    print(f"Inserted order {order.id} for {order.customer_name}")

# --- Query ---
with SessionLocal() as session:
    found = session.get(OrderModel, "ord-001")
    if found:
        print(f"Order: {found.id} | {found.customer_name} | {found.status} | £{found.total}")
        for item in found.items:
            print(f"  - {item.product_name} x{item.quantity} @ £{item.unit_price}")

    pending = session.execute(
        select(OrderModel).where(OrderModel.status == OrderStatus.PENDING)
    ).scalars().all()
    print(f"\nPending orders: {[o.id for o in pending]}")
