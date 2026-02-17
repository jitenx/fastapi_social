from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config.config import settings
from app.models.models import User
from app.database.database import get_async_db
from app.schemas.schemas import TokenData

# -------------------- CONFIG --------------------
SECRET_KEY: str = settings.secret_key
ALGORITHM: str = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# -------------------- TOKEN CREATION --------------------
def create_access_token(data: dict) -> str:
    """
    Create a JWT token with expiration time.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)


# -------------------- TOKEN VERIFICATION --------------------
def verify_access_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """
    Decode and validate JWT token.
    """
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("user_email")
        if not email:
            raise credentials_exception
        return TokenData(email=email)
    except JWTError:
        raise credentials_exception


# -------------------- GET CURRENT USER --------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """
    Dependency to get the currently authenticated user asynchronously.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    stmt = select(User).where(User.email == token_data.email)
    result = await db.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    if not user:
        raise credentials_exception
    return user
