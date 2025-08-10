from fastapi import HTTPException, status, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..schemas import schemas
from ..database.database import get_db
from ..models import models
from ..utils.utils import verify_password
from ..utils.oauth2 import create_access_token

router = APIRouter(
    tags=["Authentication"]
)


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid credentials")
    if not verify_password(user_credentials.password, str(user.password)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid credentials")
    access_token = create_access_token(data={"user_email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
