import pytest
import os
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import OperationalError

from src.orders.infrastructure.db.connection import Base
from src.orders.api.main import app, get_db

TEST_DATABASE_URL = "postgresql+psycopg://orders_user:dev_password@localhost:5433/orders_test"


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    test_engine = create_engine(TEST_DATABASE_URL)
    try:
        test_engine.connect().close()
    except OperationalError:
        if os.environ.get("CI"):
            raise  # in CI a missing DB is a real failure, never skip
        pytest.skip("Test DB not running: docker compose up -d postgres-test")
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()

