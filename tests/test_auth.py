"""
Test suite for authentication utilities.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from utils.auth import User, verify_api_key, require_role


class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(id="test-123", email="test@example.com", role="admin")
        
        assert user.id == "test-123"
        assert user.email == "test@example.com"
        assert user.role == "admin"

    def test_user_with_metadata(self):
        """Test creating a User with metadata."""
        user = User(
            id="test-456",
            email="user@example.com",
            role="api_user",
            metadata={"mode": "api_key"}
        )
        
        assert user.metadata["mode"] == "api_key"


class TestVerifyApiKey:
    """Tests for API key verification."""

    @patch('utils.auth.settings')
    def test_api_key_disabled(self, mock_settings):
        """Test that API key verification is bypassed when disabled."""
        mock_settings.API_KEY_ENABLED = False
        
        from utils.auth import verify_api_key
        
        # Should return a user without checking API key
        result = verify_api_key(api_key=None)
        
        assert result.role == "api_user"
        assert result.metadata["mode"] == "disabled"

    @patch('utils.auth.settings')
    def test_missing_api_key(self, mock_settings):
        """Test that missing API key raises 401."""
        mock_settings.API_KEY_ENABLED = True
        mock_settings.API_KEYS = ["valid-key"]
        
        from utils.auth import verify_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(api_key=None)
        
        assert exc_info.value.status_code == 401
        assert "API key is required" in exc_info.value.detail

    @patch('utils.auth.settings')
    def test_invalid_api_key(self, mock_settings):
        """Test that invalid API key raises 401."""
        mock_settings.API_KEY_ENABLED = True
        mock_settings.API_KEYS = ["valid-key"]
        
        from utils.auth import verify_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(api_key="invalid-key")
        
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.detail

    @patch('utils.auth.settings')
    def test_valid_api_key(self, mock_settings):
        """Test that valid API key returns user."""
        mock_settings.API_KEY_ENABLED = True
        mock_settings.API_KEYS = ["valid-key-1", "valid-key-2"]
        
        from utils.auth import verify_api_key
        
        result = verify_api_key(api_key="valid-key-1")
        
        assert result.role == "api_user"
        assert result.email == "api@example.com"


class TestRequireRole:
    """Tests for role-based access control."""

    @patch('utils.auth.get_current_user')
    def test_allowed_role(self, mock_get_user):
        """Test that allowed role passes through."""
        mock_user = User(id="test", email="test@test.com", role="admin")
        mock_get_user.return_value = mock_user
        
        from utils.auth import require_role
        
        checker = require_role(["admin", "developer"])
        result = checker(mock_user)
        
        assert result.role == "admin"

    @patch('utils.auth.get_current_user')
    def test_forbidden_role(self, mock_get_user):
        """Test that forbidden role raises 403."""
        mock_user = User(id="test", email="test@test.com", role="user")
        mock_get_user.return_value = mock_user
        
        from utils.auth import require_role
        
        checker = require_role(["admin"])
        
        with pytest.raises(HTTPException) as exc_info:
            checker(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
