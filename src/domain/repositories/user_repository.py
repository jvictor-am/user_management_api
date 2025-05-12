from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.domain.entities.user import User


class UserRepository(ABC):
    """Abstract interface for user repository."""

    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a user."""
        pass

    @abstractmethod
    def list_users(self, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        """List users with pagination."""
        pass
