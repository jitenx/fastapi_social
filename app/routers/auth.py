from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.utils.utils import verify_password

router = APIRouter(tags=["Authentication"])


# -------------------- LOGIN --------------------
@router.post(
    "/login", response_model=schemas.Token, status_code=status.HTTP_201_CREATED
)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Fetch user by email
    stmt = select(models.User).where(models.User.email == user_credentials.username)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not exist! Please create an account",
        )

    # Verify password
    if not verify_password(user_credentials.password, str(user.password)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect credentials",
        )

    # Generate JWT access token
    access_token = oauth2.create_access_token(data={"user_email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
