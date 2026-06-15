from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.domain.user import User
from src.auth.infrastructure.db.models import UserModel


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        db_user = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user)
        return _to_domain(db_user)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        db_user = self._session.scalars(stmt).first()
        return _to_domain(db_user) if db_user is not None else None

    def get_by_id(self, user_id: str) -> User | None:
        db_user = self._session.get(UserModel, user_id)
        return _to_domain(db_user) if db_user is not None else None


def _to_domain(db_user: UserModel) -> User:
    return User(
        id=db_user.id,
        email=db_user.email,
        password_hash=db_user.password_hash,
        created_at=db_user.created_at,
    )
