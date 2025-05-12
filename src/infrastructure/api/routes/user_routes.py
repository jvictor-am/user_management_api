from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.user_dto import UserCreate, UserResponse, UserUpdate, UsersPage
from src.application.use_cases.user_use_case import UserUseCase
from src.infrastructure.api.dependencies import get_current_user_id, get_user_use_case

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_create: UserCreate,
    user_use_case: UserUseCase = Depends(get_user_use_case),
) -> UserResponse:
    """
    Create a new user.
    
    - **username**: Unique username
    - **email**: Unique email
    - **password**: Password (will be hashed)
    """
    try:
        return user_use_case.create_user(user_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/", 
    response_model=UsersPage, 
    dependencies=[Depends(get_current_user_id)]
)
async def list_users(
    page: int = 1,
    size: int = 10,
    user_use_case: UserUseCase = Depends(get_user_use_case),
) -> UsersPage:
    """
    List all users with pagination.
    
    - **page**: Page number (starts at 1)
    - **size**: Number of items per page
    """
    if page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be >= 1")
    if size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Size must be >= 1")
        
    return user_use_case.list_users(page=page, size=size)


@router.get(
    "/{user_id}", 
    response_model=UserResponse, 
    dependencies=[Depends(get_current_user_id)]
)
async def get_user(
    user_id: int,
    user_use_case: UserUseCase = Depends(get_user_use_case),
) -> UserResponse:
    """
    Get a specific user by ID.
    
    - **user_id**: User ID
    """
    user = user_use_case.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
    return user


@router.put(
    "/{user_id}", 
    response_model=UserResponse, 
    dependencies=[Depends(get_current_user_id)]
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_use_case: UserUseCase = Depends(get_user_use_case),
) -> UserResponse:
    """
    Update a user.
    
    - **user_id**: ID of user to update
    - **user_update**: User data to update
    """
    try:
        updated_user = user_use_case.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    dependencies=[Depends(get_current_user_id)]
)
async def delete_user(
    user_id: int,
    user_use_case: UserUseCase = Depends(get_user_use_case),
) -> None:
    """
    Delete a user.
    
    - **user_id**: ID of user to delete
    """
    result = user_use_case.delete_user(user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
