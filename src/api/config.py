import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://orders_user:dev_password@localhost:5432/orders",
)
