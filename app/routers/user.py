from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.utils import utils
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/users", tags=["Users"])


# -------------------- HELPERS --------------------
def get_user_by_id(db: Session, user_id: int):
    return db.get(models.User, user_id)


def get_user_by_email(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def check_current_user(user, current_user):
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this action",
        )


# -------------------- CREATE USER --------------------
@router.post("", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user_data.password = utils.hash(user_data.password)

    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"User with email {user_data.email} already exists",
        )

    new_user = models.User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -------------------- GET USERS --------------------
@router.get("", response_model=List[schemas.UserPublic])
async def get_users(db: Session = Depends(get_db)):
    stmt = select(models.User)
    return db.execute(stmt).scalars().all()


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    check_current_user(user, current_user)
    return user


@router.get("/profile/me", response_model=schemas.UserOut)
async def get_my_profile(
    db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)
):
    user = get_user_by_email(db, current_user.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/email/{email}", response_model=schemas.UserOut)
async def get_user_by_email_endpoint(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.email != email:
        raise HTTPException(status_code=403, detail="Not authorized to view this user")
    return user


# -------------------- DELETE USER --------------------
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    user_data: schemas.UserDelete,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    check_current_user(user, current_user)

    if not utils.pwd_context.verify(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


# -------------------- UPDATE USER --------------------
@router.put("/{id}", response_model=schemas.User, status_code=status.HTTP_200_OK)
async def update_user(
    id: int,
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    check_current_user(user, current_user)

    for field, value in user_data.model_dump().items():
        if field == "password":
            value = utils.hash(user_data.password)
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
