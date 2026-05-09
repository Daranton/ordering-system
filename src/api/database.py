from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://orders_user:dev_password@localhost:5432/orders"

engine = create_engine(DATABASE_URL, echo=True) # echo=True logs SQL statements - turn off later
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass


