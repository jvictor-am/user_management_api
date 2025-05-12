from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "User Management API"
    secret_key: str = "YOUR_SECRET_KEY_HERE"  # In production, set this securely
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
