from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user_model import UserModel


class SQLiteUserRepository(UserRepository):
    """SQLite implementation of UserRepository."""

    def __init__(self, db: Session):
        self.db = db

    def _map_to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _map_to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def create(self, user: User) -> User:
        db_user = self._map_to_model(user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._map_to_entity(db_user)

    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return self._map_to_entity(db_user)
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return self._map_to_entity(db_user)
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if db_user:
            return self._map_to_entity(db_user)
        return None

    def update(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if db_user:
            db_user.username = user.username
            db_user.email = user.email
            db_user.hashed_password = user.hashed_password
            db_user.is_active = user.is_active
            db_user.updated_at = user.updated_at  # Ensure this is a datetime object
            self.db.commit()
            self.db.refresh(db_user)
            return self._map_to_entity(db_user)
        return None

    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    def list_users(self, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        total = self.db.query(UserModel).count()
        db_users = self.db.query(UserModel).order_by(UserModel.id).offset(skip).limit(limit).all()
        return [self._map_to_entity(user) for user in db_users], total
