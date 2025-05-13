from datetime import datetime, timezone
from typing import List, Optional, Tuple

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class UserService:
    """Service for user-related business logic."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user: User) -> User:
        """Create a new user."""
        existing_user = self.user_repository.get_by_email(user.email)
        if existing_user:
            raise ValueError(f"User with email {user.email} already exists")
            
        existing_username = self.user_repository.get_by_username(user.username)
        if existing_username:
            raise ValueError(f"User with username {user.username} already exists")
            
        return self.user_repository.create(user)

    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.user_repository.get_by_id(user_id)

    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update a user."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
            
        # Check for email uniqueness if email is being updated
        if "email" in user_data and user_data["email"] != user.email:
            existing_user = self.user_repository.get_by_email(user_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"User with email {user_data['email']} already exists")
                
        # Check for username uniqueness if username is being updated
        if "username" in user_data and user_data["username"] != user.username:
            existing_user = self.user_repository.get_by_username(user_data["username"])
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"User with username {user_data['username']} already exists")
                
        # Update user fields
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
                
        user.updated_at = datetime.now(timezone.utc)  # Ensure this is a datetime object
        return self.user_repository.update(user)

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return self.user_repository.delete(user_id)

    def list_users(self, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        """List users with pagination."""
        return self.user_repository.list_users(skip, limit)

    def check_account_status(self, username: str) -> Tuple[bool, Optional[str]]:
        """Check if account is locked due to too many failed attempts."""
        user = self.user_repository.get_by_username(username)
        if not user:
            return True, None  # Don't reveal that user doesn't exist
            
        # Check for lockout status (implementation would depend on your data model)
        if self._is_account_locked(user.id):
            return False, "Account is temporarily locked due to too many failed login attempts"
            
        return True, None
