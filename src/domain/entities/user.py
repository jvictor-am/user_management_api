from datetime import datetime, timezone
from typing import Optional


class User:
    """User entity representing a user in the domain."""

    def __init__(
        self,
        id: Optional[int] = None,
        username: str = "",
        email: str = "",
        hashed_password: str = "",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
