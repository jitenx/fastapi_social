from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Initialize Argon2 password hasher
pwd_context = PasswordHash((Argon2Hasher(),))


def hash(password: str) -> str:
    """
    Hash a plain text password using Argon2.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    """
    return pwd_context.verify(password, hashed_password)
