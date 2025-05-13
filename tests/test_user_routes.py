import pytest
from fastapi import status
from unittest.mock import MagicMock, patch

def test_update_user(client, monkeypatch):
    """Test updating a user."""
    # Create a test user first
    create_data = {
        "username": "updateuser", 
        "email": "update@example.com", 
        "password": "Password123!"
    }
    response = client.post("/users/", json=create_data)
    user_id = response.json()["id"]
    
    # Login to get token
    login_response = client.post(
        "/auth/login/json", 
        json={"username": "updateuser", "password": "Password123!"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test partial update
    update_data = {"username": "updateduser"}
    response = client.put(f"/users/{user_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"
    
    # Test not found
    response = client.put(f"/users/999", headers=headers, json=update_data)
    assert response.status_code == 404

def test_delete_user(client):
    """Test deleting a user."""
    # Create a test user first
    create_data = {
        "username": "deleteuser", 
        "email": "delete@example.com", 
        "password": "Password123!"
    }
    response = client.post("/users/", json=create_data)
    user_id = response.json()["id"]
    
    # Login to get token
    login_response = client.post(
        "/auth/login/json", 
        json={"username": "deleteuser", "password": "Password123!"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Delete the user
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 404
