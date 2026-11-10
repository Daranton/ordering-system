# tests/conftest.py
import os

# Unit tests import modules that read DATABASE_URL at import time;
# give them a default so a fresh clone runs without a .env file.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://orders_user:dev_password@localhost:5433/orders_test",
)