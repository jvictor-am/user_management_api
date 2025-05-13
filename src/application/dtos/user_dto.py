from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(
        ..., 
        min_length=8,
        # Remove lookahead assertions which aren't supported
        # Instead, we'll validate this in a separate validator
        description="Password must be at least 8 characters and include uppercase, lowercase, number and special character"
    )
    
    # Add a validator for password complexity
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        has_lowercase = any(c.islower() for c in v)
        has_uppercase = any(c.isupper() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "@$!%*?&#" for c in v)
        
        if not (has_lowercase and has_uppercase and has_digit and has_special):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )
        
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UsersPage(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserLogin(BaseModel):
    username: str
    password: str
