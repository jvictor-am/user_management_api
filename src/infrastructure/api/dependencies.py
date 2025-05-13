from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.application.dtos.user_dto import TokenPayload
from src.application.use_cases.auth_use_case import AuthUseCase
from src.application.use_cases.user_use_case import UserUseCase
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.auth_service import AuthService
from src.domain.services.user_service import UserService
from src.infrastructure.database.database import get_db
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.infrastructure.repositories.sqlite_auth_log_repository import SQLiteAuthLogRepository
from src.settings import Settings

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SQLiteUserRepository(db)


def get_auth_log_repository(db: Session = Depends(get_db)) -> SQLiteAuthLogRepository:
    """Return an AuthLogRepository implementation."""
    return SQLiteAuthLogRepository(db)


def get_auth_service(auth_log_repository: SQLiteAuthLogRepository = Depends(get_auth_log_repository)) -> AuthService:
    """Return an AuthService instance."""
    settings = Settings()
    return AuthService(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        auth_log_repository=auth_log_repository
    )


def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)


def get_auth_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthUseCase:
    return AuthUseCase(user_repository, auth_service)


def get_user_use_case(
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserUseCase:
    return UserUseCase(user_service, auth_service)


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, auth_service.secret_key, algorithms=[auth_service.algorithm]
        )
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            raise credentials_exception
            
        token_payload = TokenPayload(sub=user_id_str, exp=payload.get("exp"))
        
        current_timestamp = datetime.now(timezone.utc).timestamp()
        if token_payload.exp < current_timestamp:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    return int(token_payload.sub)
