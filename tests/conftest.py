import os
import pytest
from typing import Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.infrastructure.database.database import Base
from src.infrastructure.database.models.user_model import UserModel
from src.domain.services.user_service import UserService
from src.domain.services.auth_service import AuthService
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.application.use_cases.user_use_case import UserUseCase
from src.application.use_cases.auth_use_case import AuthUseCase
from src.infrastructure.api.dependencies import get_db, get_user_repository
from src.infrastructure.api.dependencies import get_auth_use_case, get_user_use_case
from src.settings import Settings

# Set testing environment
os.environ["TESTING"] = "1"

# Create a completely separate in-memory database for testing
# Use StaticPool to ensure the same connection is used throughout tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create tables in the test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database session for each test.
    """
    connection = test_engine.connect()
    # Begin a non-ORM transaction
    transaction = connection.begin()
    
    # Create a session bound to the connection
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Rollback the transaction and close the connection
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Create a new FastAPI TestClient that uses the `db` fixture.
    """
    from src.main import app
    
    # Create test dependencies
    def override_get_db():
        yield db
        
    def override_get_user_repository():
        return SQLiteUserRepository(db)
        
    def override_get_auth_service():
        settings = Settings()
        return AuthService(
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            access_token_expire_minutes=settings.access_token_expire_minutes,
        )
        
    def override_get_user_service():
        return UserService(override_get_user_repository())
        
    def override_get_auth_use_case():
        return AuthUseCase(
            override_get_user_repository(),
            override_get_auth_service()
        )
        
    def override_get_user_use_case():
        return UserUseCase(
            override_get_user_service(),
            override_get_auth_service()
        )
    
    # Override all dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_repository] = override_get_user_repository
    app.dependency_overrides[get_auth_use_case] = override_get_auth_use_case
    app.dependency_overrides[get_user_use_case] = override_get_user_use_case
    
    with TestClient(app) as test_client:
        yield test_client
        
    # Clear all overrides after test
    app.dependency_overrides = {}
