"""Authentication service using BetterAuth-style JWT authentication.

Provides user registration, login, and session management.
"""

from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.user import User

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
ALGORITHM = "HS256"


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize auth service with database session.

        Args:
            db: Async database session.
        """
        self.db = db

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password.

        Args:
            password: Plaintext password.

        Returns:
            Hashed password string.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plaintext password to verify.
            hashed_password: Stored password hash.

        Returns:
            True if password matches, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        user_id: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a JWT access token.

        Args:
            user_id: User ID to encode in token.
            expires_delta: Optional custom expiration time.

        Returns:
            Encoded JWT token string.
        """
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.session_expire_minutes)
        )
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(to_encode, settings.better_auth_secret, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict | None:
        """Decode and validate a JWT token.

        Args:
            token: JWT token string.

        Returns:
            Decoded token payload or None if invalid.
        """
        try:
            payload = jwt.decode(
                token, settings.better_auth_secret, algorithms=[ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email address.

        Args:
            email: Email address to look up.

        Returns:
            User object or None if not found.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by ID.

        Args:
            user_id: User ID to look up.

        Returns:
            User object or None if not found.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def register(
        self,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> User:
        """Register a new user.

        Args:
            email: User's email address.
            password: User's plaintext password.
            display_name: Optional display name.

        Returns:
            Created User object.

        Raises:
            ValueError: If email is already registered.
        """
        existing = await self.get_user_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=email.lower().strip(),
            password_hash=self.hash_password(password),
            display_name=display_name,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user with email and password.

        Args:
            email: User's email address.
            password: User's plaintext password.

        Returns:
            User object if authentication succeeds, None otherwise.
        """
        user = await self.get_user_by_email(email.lower().strip())
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    async def login(self, email: str, password: str) -> tuple[User, str] | None:
        """Login a user and return an access token.

        Args:
            email: User's email address.
            password: User's plaintext password.

        Returns:
            Tuple of (User, token) if successful, None otherwise.
        """
        user = await self.authenticate(email, password)
        if not user:
            return None
        token = self.create_access_token(user.id)
        return user, token
