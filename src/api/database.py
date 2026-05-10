from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.api.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True) # echo=True logs SQL statements - turn off later
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass


