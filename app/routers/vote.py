from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2
from app.database.database import get_async_db
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/vote", tags=["Vote"])


# -------------------- HELPERS --------------------
async def get_post(db: AsyncSession, post_id: int):
    stmt = select(models.Post).where(models.Post.id == post_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_vote(db: AsyncSession, post_id: int, user_id: int):
    stmt = select(models.Vote).where(
        models.Vote.post_id == post_id, models.Vote.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# -------------------- VOTE ENDPOINT --------------------
@router.post("", status_code=status.HTTP_201_CREATED)
async def vote(
    vote: schemas.Vote,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    # Ensure post exists
    post = await get_post(db, vote.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Check existing vote
    existing_vote = await get_user_vote(db, vote.post_id, current_user.id)

    if vote.dir == 1:  # Add vote
        if existing_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already voted on post {vote.post_id}",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        await db.commit()
        return {"message": "Successfully voted"}

    else:  # Remove vote
        if not existing_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You have not voted on this post",
            )
        stmt = delete(models.Vote).where(
            models.Vote.post_id == vote.post_id,
            models.Vote.user_id == current_user.id,
        )
        await db.execute(stmt)
        await db.commit()
        return {"message": "Vote removed successfully"}
