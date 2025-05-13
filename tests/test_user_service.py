from datetime import datetime
import pytest

from src.domain.entities.user import User
from src.domain.services.user_service import UserService


class MockUserRepository:
    def __init__(self):
        self.users = {}
        self.next_id = 1
        
    def create(self, user):
        user.id = self.next_id
        self.next_id += 1
        self.users[user.id] = user
        return user
        
    def get_by_id(self, user_id):
        return self.users.get(user_id)
        
    def get_by_email(self, email):
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_by_username(self, username):
        for user in self.users.values():
            if user.username == username:
                return user
        return None
        
    def update(self, user):
        if user.id in self.users:
            self.users[user.id] = user
            return user
        return None
        
    def delete(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
        
    def list_users(self, skip, limit):
        all_users = list(self.users.values())
        return all_users[skip:skip+limit], len(all_users)


@pytest.fixture
def user_repository():
    return MockUserRepository()


@pytest.fixture
def user_service(user_repository):
    return UserService(user_repository)


def test_create_user(user_service):
    # Create a test user
    user = User(username="test", email="test@example.com", hashed_password="hashed_pw")
    created_user = user_service.create_user(user)
    
    # Check if user was created correctly
    assert created_user.id == 1
    assert created_user.username == "test"
    assert created_user.email == "test@example.com"
    
    # Test duplicate email
    duplicate_user = User(username="test2", email="test@example.com", hashed_password="hashed_pw")
    with pytest.raises(ValueError):
        user_service.create_user(duplicate_user)
        
    # Test duplicate username
    duplicate_user = User(username="test", email="test2@example.com", hashed_password="hashed_pw")
    with pytest.raises(ValueError):
        user_service.create_user(duplicate_user)


def test_get_user(user_service, user_repository):
    # Create a test user first
    user = User(username="test", email="test@example.com", hashed_password="hashed_pw")
    created_user = user_repository.create(user)
    
    # Get the user
    found_user = user_service.get_user(created_user.id)
    assert found_user is not None
    assert found_user.username == "test"
    
    # Test non-existent user
    non_existent = user_service.get_user(999)
    assert non_existent is None


def test_update_user(user_service, user_repository):
    # Create a test user
    user = User(username="test", email="test@example.com", hashed_password="hashed_pw")
    created_user = user_repository.create(user)
    
    # Update the user
    update_data = {"username": "updated", "email": "updated@example.com"}
    updated_user = user_service.update_user(created_user.id, update_data)
    
    # Check if user was updated correctly
    assert updated_user.username == "updated"
    assert updated_user.email == "updated@example.com"
    
    # Test updating non-existent user
    updated_user = user_service.update_user(999, update_data)
    assert updated_user is None


def test_delete_user(user_service, user_repository):
    # Create a test user
    user = User(username="test", email="test@example.com", hashed_password="hashed_pw")
    created_user = user_repository.create(user)
    
    # Delete the user
    result = user_service.delete_user(created_user.id)
    assert result is True
    
    # Check if user was deleted
    deleted_user = user_service.get_user(created_user.id)
    assert deleted_user is None
    
    # Test deleting non-existent user
    result = user_service.delete_user(999)
    assert result is False


def test_list_users(user_service, user_repository):
    # Create some test users
    for i in range(15):
        user = User(username=f"test{i}", email=f"test{i}@example.com", hashed_password="hashed_pw")
        user_repository.create(user)
    
    # Test pagination
    users_page1, total1 = user_service.list_users(skip=0, limit=10)
    assert len(users_page1) == 10
    assert total1 == 15
    
    users_page2, total2 = user_service.list_users(skip=10, limit=10)
    assert len(users_page2) == 5
    assert total2 == 15


def test_update_user_partial_fields(user_service, user_repository):
    # Create a test user
    user = User(username="test", email="test@example.com", hashed_password="hashed_pw")
    created_user = user_repository.create(user)
    
    # Update only username
    username_update = {"username": "updated_username"}
    updated_user = user_service.update_user(created_user.id, username_update)
    assert updated_user.username == "updated_username"
    assert updated_user.email == "test@example.com"
    
    # Update only email
    email_update = {"email": "newemail@example.com"}
    updated_user = user_service.update_user(created_user.id, email_update)
    assert updated_user.username == "updated_username"
    assert updated_user.email == "newemail@example.com"
    
    # Update is_active status
    status_update = {"is_active": False}
    updated_user = user_service.update_user(created_user.id, status_update)
    assert updated_user.is_active is False


def test_update_user_with_existing_email(user_service, user_repository):
    # Create two test users
    user1 = User(username="user1", email="user1@example.com", hashed_password="hashed_pw")
    user2 = User(username="user2", email="user2@example.com", hashed_password="hashed_pw")
    user_repository.create(user1)
    user_repository.create(user2)
    
    # Try to update user2 with user1's email
    update_data = {"email": "user1@example.com"}
    
    # This should raise a ValueError since we modified the service to validate emails on update
    with pytest.raises(ValueError):
        user_service.update_user(user2.id, update_data)
    
    # Verify the email hasn't been changed
    updated_user = user_service.get_user(user2.id)
    assert updated_user.email == "user2@example.com"


def test_update_user_timestamp(user_service, user_repository):
    # Create a test user
    user = User(username="test", email="test@example.com", hashed_password="hashed_pw")
    created_user = user_repository.create(user)
    initial_updated_at = created_user.updated_at
    
    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(0.001)
    
    # Update the user
    update_data = {"username": "updated"}
    updated_user = user_service.update_user(created_user.id, update_data)
    
    # Check if updated_at timestamp was changed
    # Handle both datetime objects and float timestamps
    if isinstance(initial_updated_at, datetime):
        # Convert datetime to timestamp if needed
        initial_ts = initial_updated_at.timestamp()
        updated_ts = updated_user.updated_at.timestamp() if isinstance(updated_user.updated_at, datetime) else updated_user.updated_at
    else:
        # Both are already timestamps (floats)
        initial_ts = initial_updated_at
        updated_ts = updated_user.updated_at
        
    assert updated_ts > initial_ts, "Updated timestamp should be greater than initial timestamp"


def test_list_users_empty_repository(user_service):
    # Test pagination with empty repository
    users, total = user_service.list_users(skip=0, limit=10)
    assert len(users) == 0
    assert total == 0


def test_list_users_skip_exceeds_total(user_service, user_repository):
    # Create a few test users
    for i in range(5):
        user = User(username=f"test{i}", email=f"test{i}@example.com", hashed_password="hashed_pw")
        user_repository.create(user)
    
    # Test when skip exceeds total users
    users, total = user_service.list_users(skip=10, limit=10)
    assert len(users) == 0
    assert total == 5


def test_list_users_zero_limit(user_service, user_repository):
    # Create a few test users
    for i in range(5):
        user = User(username=f"test{i}", email=f"test{i}@example.com", hashed_password="hashed_pw")
        user_repository.create(user)
    
    # Test with limit=0
    users, total = user_service.list_users(skip=0, limit=0)
    assert len(users) == 0
    assert total == 5


def test_create_user_with_existing_inactive_user(user_service, user_repository):
    # Create an inactive user
    inactive_user = User(username="inactive", email="inactive@example.com", 
                         hashed_password="hashed_pw", is_active=False)
    user_repository.create(inactive_user)
    
    # Try to create a new user with the same username
    new_user = User(username="inactive", email="different@example.com", hashed_password="hashed_pw")
    
    # Current implementation will still reject this even though the existing user is inactive
    with pytest.raises(ValueError):
        user_service.create_user(new_user)
