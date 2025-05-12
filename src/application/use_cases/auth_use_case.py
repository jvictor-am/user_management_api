from typing import Optional

from src.application.dtos.user_dto import Token
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.auth_service import AuthService


class AuthUseCase:
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service

    def authenticate(self, username: str, password: str) -> Optional[Token]:
        """Authenticate user and return token."""
        user = self.user_repository.get_by_username(username)
        if not user:
            return None

        user = self.auth_service.authenticate_user(user, password)
        if not user:
            return None

        access_token = self.auth_service.create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token, token_type="bearer")
