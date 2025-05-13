import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from src.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.infrastructure.database.models.user_model import UserModel

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    return session

@pytest.fixture
def user_repository(mock_db_session):
    """Create a SQLiteUserRepository with a mock session."""
    return SQLiteUserRepository(mock_db_session)

def test_update_nonexistent_user(user_repository, mock_db_session):
    """Test updating a user that doesn't exist."""
    # Mock the query to return None (user not found)
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db_session.query.return_value = mock_query
    
    # Create a test user
    user = User(id=999, username="nonexistent", email="nonexistent@example.com")
    
    # Update should return None for non-existent user
    result = user_repository.update(user)
    assert result is None

def test_delete_nonexistent_user(user_repository, mock_db_session):
    """Test deleting a user that doesn't exist."""
    # Mock the query to return None (user not found)
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db_session.query.return_value = mock_query
    
    # Delete should return False for non-existent user
    result = user_repository.delete(999)
    assert result is False
