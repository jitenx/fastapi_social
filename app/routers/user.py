from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2
from app.utils import utils
from app.database.database import get_async_db  # async session dependency
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/users", tags=["Users"])


# -------------------- HELPERS --------------------
async def get_user_by_id(db: AsyncSession, user_id: int):
    return await db.get(models.User, user_id)


async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def check_current_user(user, current_user):
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this action",
        )


# -------------------- CREATE USER --------------------
@router.post("", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)
):
    user_data.password = utils.hash(user_data.password)

    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"User with email {user_data.email} already exists",
        )

    new_user = models.User(**user_data.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# -------------------- GET USERS --------------------
@router.get("", response_model=List[schemas.UserPublic])
async def get_users(db: AsyncSession = Depends(get_async_db)):
    stmt = select(models.User)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = await get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    check_current_user(user, current_user)
    return user


@router.get("/profile/me", response_model=schemas.UserOut)
async def get_my_profile(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = await get_user_by_email(db, current_user.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------- DELETE USER --------------------
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    user_data: schemas.UserDelete,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = await get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    check_current_user(user, current_user)

    if not utils.pwd_context.verify(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    await db.delete(user)
    await db.commit()


# -------------------- PATCH USER --------------------
@router.patch("/{id}", response_model=schemas.User)
async def patch_user(
    id: int,
    user_data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    user = await get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    check_current_user(user, current_user)

    update_data = user_data.model_dump(exclude_unset=True)

    # If password is being updated → require current_password
    if "password" in update_data:
        if not user_data.current_password:
            raise HTTPException(
                status_code=400,
                detail="Current password required",
            )

        if not utils.pwd_context.verify(user_data.current_password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect",
            )

        update_data["password"] = utils.hash(update_data["password"])

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user
