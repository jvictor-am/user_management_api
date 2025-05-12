import pytest
from jose import jwt
from datetime import timedelta, datetime, timezone

from src.domain.entities.user import User
from src.domain.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    return AuthService(secret_key="test_secret_key", algorithm="HS256", access_token_expire_minutes=30)


def test_password_hashing(auth_service):
    password = "my_secure_password"
    hashed = auth_service.get_password_hash(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Hash should be verifiable
    assert auth_service.verify_password(password, hashed)
    
    # Wrong password should fail
    assert not auth_service.verify_password("wrong_password", hashed)


def test_token_creation(auth_service):
    data = {"sub": "1"}
    token = auth_service.create_access_token(data)
    
    # Token should be a non-empty string
    assert token
    assert isinstance(token, str)
    
    # Token should be decodable and contain the expected data
    payload = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
    assert payload["sub"] == "1"
    assert "exp" in payload


def test_user_authentication(auth_service):
    # Create a user with a hashed password
    password = "my_secure_password"
    hashed_password = auth_service.get_password_hash(password)
    user = User(id=1, username="test", email="test@example.com", hashed_password=hashed_password)
    
    # Authentication should succeed with correct password
    authenticated_user = auth_service.authenticate_user(user, password)
    assert authenticated_user
    assert authenticated_user.id == user.id
    
    # Authentication should fail with incorrect password
    assert auth_service.authenticate_user(user, "wrong_password") is None
    
    # Authentication should fail with None user
    assert auth_service.authenticate_user(None, password) is None


def test_token_expiration(auth_service):
    # Test token with custom expiration
    data = {"sub": "1"}
    
    # Create token with 5 minutes expiration
    token = auth_service.create_access_token(data, expires_delta=timedelta(minutes=5))
    payload = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
    
    # Check expiration time is approximately 5 minutes from now
    now = datetime.now(timezone.utc).timestamp()
    assert abs((payload["exp"] - now) - 300) < 10  # Should be close to 300 seconds (5 minutes)
    
    # Create token with default expiration
    token = auth_service.create_access_token(data)
    payload = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
    
    # Check expiration time is approximately 30 minutes from now (default)
    assert abs((payload["exp"] - now) - 1800) < 10  # Should be close to 1800 seconds (30 minutes)


def test_different_password_hashing_results(auth_service):
    # Verify that hashing the same password twice produces different hashes (due to salting)
    password = "same_password"
    hash1 = auth_service.get_password_hash(password)
    hash2 = auth_service.get_password_hash(password)
    
    # Hashes should be different due to random salt
    assert hash1 != hash2
    
    # But both should verify correctly
    assert auth_service.verify_password(password, hash1)
    assert auth_service.verify_password(password, hash2)


def test_inactive_user_authentication(auth_service):
    # Test authentication with an inactive user
    password = "my_secure_password"
    hashed_password = auth_service.get_password_hash(password)
    inactive_user = User(
        id=1, 
        username="inactive", 
        email="inactive@example.com", 
        hashed_password=hashed_password,
        is_active=False
    )
    
    # The current implementation doesn't check for is_active status during authentication
    # This test documents current behavior
    authenticated_user = auth_service.authenticate_user(inactive_user, password)
    assert authenticated_user is not None
    assert authenticated_user.is_active is False


def test_token_with_additional_claims(auth_service):
    # Test creating a token with additional claims
    data = {
        "sub": "1",
        "username": "testuser",
        "roles": ["user", "admin"]
    }
    token = auth_service.create_access_token(data)
    
    # Decode and verify all claims are present
    payload = jwt.decode(token, auth_service.secret_key, algorithms=[auth_service.algorithm])
    assert payload["sub"] == "1"
    assert payload["username"] == "testuser"
    assert "admin" in payload["roles"]
    assert "user" in payload["roles"]
