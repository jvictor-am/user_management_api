from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from jose import jwt
from passlib.context import CryptContext

from src.domain.entities.user import User
from src.domain.repositories.auth_log_repository import AuthLogRepository


class AuthService:
    """Service for handling authentication related operations."""

    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 access_token_expire_minutes: int = 30,
                 auth_log_repository: Optional[AuthLogRepository] = None):
        # Updated to use Argon2 as primary with bcrypt as fallback for existing hashes
        self.pwd_context = CryptContext(
            schemes=["argon2", "bcrypt"],
            default="argon2",
            argon2__time_cost=2,      # Number of iterations
            argon2__memory_cost=65536, # Memory usage in kibibytes (64MB)
            argon2__parallelism=4,     # Parallelism factor
            deprecated="auto"
        )
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.auth_log_repository = auth_log_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a new JWT token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        
        # Add JWT ID to prevent token reuse
        jti = str(uuid.uuid4())
        to_encode.update({"jti": jti})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def authenticate_user(self, user: Optional[User], password: str, ip_address: str = None) -> Optional[User]:
        # Track login attempts
        if not user:
            # Log failed attempt for non-existent user
            self._log_failed_attempt(None, ip_address)
            return None
        
        if not self.verify_password(password, user.hashed_password):
            # Log failed attempt for existing user
            self._log_failed_attempt(user.id, ip_address)
            return None
            
        # Log successful login
        self._log_successful_login(user.id, ip_address)
        return user
    
    def _log_failed_attempt(self, user_id: Optional[int], ip_address: Optional[str]) -> None:
        """Log a failed authentication attempt."""
        if self.auth_log_repository:
            details = "Invalid credentials"
            if not user_id:
                details = "User not found"
                
            self.auth_log_repository.add_log(
                user_id=user_id,
                ip_address=ip_address,
                success=False,
                details=details
            )

    def _log_successful_login(self, user_id: int, ip_address: Optional[str]) -> None:
        """Log a successful authentication."""
        if self.auth_log_repository:
            self.auth_log_repository.add_log(
                user_id=user_id,
                ip_address=ip_address,
                success=True
            )
