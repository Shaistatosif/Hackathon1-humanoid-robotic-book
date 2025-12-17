"""Unit tests for AuthService."""

from datetime import timedelta

import pytest

from src.services.auth_service import AuthService


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_hash_password_returns_hash(self):
        """Test that hash_password returns a hashed string."""
        password = "secure_password123"
        hashed = AuthService.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_hash_password_different_for_same_input(self):
        """Test that same password produces different hashes (salt)."""
        password = "secure_password123"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that correct password is verified."""
        password = "secure_password123"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification."""
        password = "secure_password123"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password("wrong_password", hashed) is False

    def test_verify_password_empty(self):
        """Test that empty password fails verification."""
        password = "secure_password123"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password("", hashed) is False


class TestJWTTokens:
    """Tests for JWT token functionality."""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        token = AuthService.create_access_token("user-123")

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_different_users(self):
        """Test that different users get different tokens."""
        token1 = AuthService.create_access_token("user-123")
        token2 = AuthService.create_access_token("user-456")

        assert token1 != token2

    def test_decode_token_valid(self):
        """Test decoding a valid token."""
        user_id = "user-123"
        token = AuthService.create_access_token(user_id)
        payload = AuthService.decode_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_decode_token_invalid(self):
        """Test decoding an invalid token returns None."""
        payload = AuthService.decode_token("invalid.token.here")

        assert payload is None

    def test_decode_token_empty(self):
        """Test decoding an empty token returns None."""
        payload = AuthService.decode_token("")

        assert payload is None

    def test_create_access_token_custom_expiry(self):
        """Test token with custom expiration time."""
        token = AuthService.create_access_token(
            "user-123",
            expires_delta=timedelta(hours=1),
        )
        payload = AuthService.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "user-123"


@pytest.mark.asyncio
class TestAuthServiceDatabase:
    """Tests for AuthService database operations."""

    async def test_register_new_user(self, db_session):
        """Test registering a new user."""
        service = AuthService(db_session)
        user = await service.register(
            email="test@example.com",
            password="password123",
            display_name="Test User",
        )

        assert user is not None
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        assert user.password_hash != "password123"

    async def test_register_duplicate_email_raises(self, db_session):
        """Test that registering duplicate email raises ValueError."""
        service = AuthService(db_session)
        await service.register(
            email="test@example.com",
            password="password123",
        )

        with pytest.raises(ValueError, match="Email already registered"):
            await service.register(
                email="test@example.com",
                password="password456",
            )

    async def test_register_normalizes_email(self, db_session):
        """Test that email is normalized on registration."""
        service = AuthService(db_session)
        user = await service.register(
            email="  TEST@EXAMPLE.COM  ",
            password="password123",
        )

        assert user.email == "test@example.com"

    async def test_get_user_by_email_found(self, db_session):
        """Test getting a user by email."""
        service = AuthService(db_session)
        await service.register(
            email="test@example.com",
            password="password123",
        )

        user = await service.get_user_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"

    async def test_get_user_by_email_not_found(self, db_session):
        """Test getting a non-existent user by email."""
        service = AuthService(db_session)
        user = await service.get_user_by_email("notfound@example.com")

        assert user is None

    async def test_authenticate_correct_credentials(self, db_session):
        """Test authentication with correct credentials."""
        service = AuthService(db_session)
        await service.register(
            email="test@example.com",
            password="password123",
        )

        user = await service.authenticate("test@example.com", "password123")
        assert user is not None
        assert user.email == "test@example.com"

    async def test_authenticate_wrong_password(self, db_session):
        """Test authentication with wrong password."""
        service = AuthService(db_session)
        await service.register(
            email="test@example.com",
            password="password123",
        )

        user = await service.authenticate("test@example.com", "wrongpassword")
        assert user is None

    async def test_authenticate_nonexistent_user(self, db_session):
        """Test authentication with non-existent user."""
        service = AuthService(db_session)
        user = await service.authenticate("notfound@example.com", "password123")

        assert user is None

    async def test_login_successful(self, db_session):
        """Test successful login returns user and token."""
        service = AuthService(db_session)
        await service.register(
            email="test@example.com",
            password="password123",
        )

        result = await service.login("test@example.com", "password123")
        assert result is not None
        user, token = result
        assert user.email == "test@example.com"
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_login_failed(self, db_session):
        """Test failed login returns None."""
        service = AuthService(db_session)
        await service.register(
            email="test@example.com",
            password="password123",
        )

        result = await service.login("test@example.com", "wrongpassword")
        assert result is None
