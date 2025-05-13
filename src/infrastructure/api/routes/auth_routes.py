from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.application.dtos.user_dto import Token, UserLogin
from src.application.use_cases.auth_use_case import AuthUseCase
from src.infrastructure.api.dependencies import get_auth_use_case

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case),
) -> Token:
    """
    Login endpoint to obtain JWT token.
    
    - **username**: Username
    - **password**: Password
    """
    token = auth_use_case.authenticate(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.post("/login/json", response_model=Token)
async def login_json(
    user_login: UserLogin,
    auth_use_case: AuthUseCase = Depends(get_auth_use_case),
) -> Token:
    """
    Login endpoint with JSON body to obtain JWT token.
    
    - **username**: Username
    - **password**: Password
    """
    token = auth_use_case.authenticate(user_login.username, user_login.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
