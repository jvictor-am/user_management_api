import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_user_and_login(client):
    """Test creating a user and then logging in using the test client fixture."""
    # Create a user
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }
    
    # Use the client fixture from conftest.py which has the DB dependencies properly overridden
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    
    # Login with the created user
    login_data = {
        "username": "testuser",
        "password": "password123"
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

def test_rate_limiting(client):
    """Test that the rate limiting middleware works correctly."""
    # The rate limiter might already have some counts from previous tests
    # So we'll make fewer requests and just verify the limiter works eventually
    
    # Make several requests - should be allowed
    for i in range(5):
        response = client.get("/")
        assert response.status_code == 200
    
    # Now keep making requests until we hit the limit or reach a maximum try count
    hit_limit = False
    for i in range(30):  # Try up to 30 more times
        response = client.get("/")
        if response.status_code == 429:
            hit_limit = True
            assert response.text == "Rate limit exceeded"
            break
    
    # Verify we did hit the rate limit
    assert hit_limit, "Rate limiting didn't trigger"
