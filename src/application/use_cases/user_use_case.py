from typing import Optional

from src.application.dtos.user_dto import UserCreate, UserResponse, UserUpdate, UsersPage
from src.domain.entities.user import User
from src.domain.services.auth_service import AuthService
from src.domain.services.user_service import UserService


class UserUseCase:
    def __init__(self, user_service: UserService, auth_service: AuthService):
        self.user_service = user_service
        self.auth_service = auth_service

    def create_user(self, user_create: UserCreate) -> UserResponse:
        """Create a new user."""
        hashed_password = self.auth_service.get_password_hash(user_create.password)
        
        user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )
        
        created_user = self.user_service.create_user(user)
        
        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )

    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Get a user by ID."""
        user = self.user_service.get_user(user_id)
        
        if not user:
            return None
            
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        """Update a user."""
        update_data = user_update.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = self.auth_service.get_password_hash(update_data.pop("password"))
            
        updated_user = self.user_service.update_user(user_id, update_data)
        
        if not updated_user:
            return None
            
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return self.user_service.delete_user(user_id)

    def list_users(self, page: int = 1, size: int = 10) -> UsersPage:
        """List users with pagination."""
        skip = (page - 1) * size
        users, total = self.user_service.list_users(skip=skip, limit=size)
        
        total_pages = (total + size - 1) // size
        
        items = [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ]
        
        return UsersPage(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=total_pages,
        )
