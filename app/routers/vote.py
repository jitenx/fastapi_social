from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/vote", tags=["Vote"])


# -------------------- HELPERS --------------------
def get_post(db: Session, post_id: int):
    stmt = select(models.Post).where(models.Post.id == post_id)
    return db.execute(stmt).scalar_one_or_none()


def get_user_vote(db: Session, post_id: int, user_id: int):
    stmt = select(models.Vote).where(
        models.Vote.post_id == post_id, models.Vote.user_id == user_id
    )
    return db.execute(stmt).scalar_one_or_none()


# -------------------- VOTE ENDPOINT --------------------
@router.post("", status_code=status.HTTP_201_CREATED)
async def vote(
    vote: schemas.Vote,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post = get_post(db, vote.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    existing_vote = get_user_vote(db, vote.post_id, current_user.id)

    # Add vote
    if vote.dir == 1:
        if existing_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already voted on post {vote.post_id}",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully voted"}

    # Remove vote
    else:
        if not existing_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You have not voted on this post",
            )
        stmt = delete(models.Vote).where(models.Vote.id == existing_vote.id)
        db.execute(stmt)
        db.commit()
        return {"message": "Vote removed successfully"}
