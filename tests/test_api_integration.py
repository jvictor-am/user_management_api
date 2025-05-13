import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_user_and_login(client):
    """Test creating a user and then logging in using the test client fixture."""
    # Create a user with a complex password that passes validation
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Password123!"  # Complex password with upper, lower, number, special char
    }
    
    # Use the client fixture from conftest.py which has the DB dependencies properly overridden
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    
    # Login with the created user
    login_data = {
        "username": "testuser",
        "password": "Password123!"
    }
    response = client.post("/auth/login/json", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Use the token to access protected endpoint
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert "items" in response.json()

def test_get_user_by_id(client):
    """Test retrieving a user by ID."""
    # Create a test user first
    user_data = {"username": "getuser", "email": "getuser@example.com", "password": "Password123!"}
    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]
    
    # Login to get token
    login_data = {"username": "getuser", "password": "Password123!"}
    response = client.post("/auth/login/json", json=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user by ID
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == "getuser"

def test_password_validation(client):
    """Test password validation rules."""
    # Test with weak password
    user_data = {"username": "weakpass", "email": "weak@example.com", "password": "simple"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422  # Validation error
    
    # Test with strong password
    user_data["password"] = "StrongP@ss123"
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
