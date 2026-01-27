from typing import List
from fastapi import HTTPException, status, Depends, APIRouter

from app.auth import oauth2
from app.utils import utils

from app.database.database import get_db
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password
    user.password = utils.hash(user.password)
    new_user = models.User(**user.model_dump())
    user = db.query(models.User).filter(models.User.email == new_user.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"User with email: {new_user.email} already exists",
        )
    # user_phone = (
    #     db.query(models.User)
    #     .filter(models.User.phone_number == new_user.phone_number)
    #     .first()
    # )
    # if user_phone:
    #     raise HTTPException(
    #         status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #         detail=f"User with phone number: {new_user.phone_number} already exists",
    #     )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("", response_model=List[schemas.UserPublic])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user1(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email: {id} is not found",
        )
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Not authorized to view this user",
        )
    return user


@router.get("/profile/me", response_model=schemas.UserOut)
async def get_user(
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    
    return user

@router.get("/email/{email}", response_model=schemas.UserOut)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email: {email} is not found",
        )
    if current_user.email != email:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Not authorized to view this user",
        )
    return user


@router.delete("/email/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email: {email} is not found",
        )
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    db.delete(user)
    db.commit()
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} is not found",
        )
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )
    db.delete(user)
    db.commit()
    return user


@router.put("/{id}", response_model=schemas.User, status_code=status.HTTP_200_OK)
async def update_user(
    id: int,
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email: {id} is not found",
        )
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )
    for field, value in user_data.model_dump().items():
        if field == "password":
            value = utils.hash(user_data.password)
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.put(
    "/email/{email}", response_model=schemas.User, status_code=status.HTTP_200_OK
)
async def update_user_by_email(
    email: str,
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email: {id} is not found",
        )
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )
    for field, value in user_data.model_dump().items():
        if field == "password":
            value = utils.hash(user_data.password)
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
