from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

import app.models.models as models
import app.schemas.schemas as schemas
import app.auth.oauth2 as oauth2
from app.database.database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


# -------------------- HELPERS --------------------
def format_post_with_votes(post_row, current_user_id):
    post, votes, user_voted_count = post_row
    return {
        "Post": post,
        "votes": votes,
        "user_voted": bool(user_voted_count),
    }


def get_posts_query(current_user_id: int, search: str = "", owner_only: bool = False):
    stmt = select(
        models.Post,
        func.count(models.Vote.post_id).label("votes"),
        func.count(func.nullif(models.Vote.user_id != current_user_id, True)).label(
            "user_voted"
        ),
    ).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)

    if owner_only:
        stmt = stmt.where(models.Post.owner_id == current_user_id)
    else:
        stmt = stmt.where(
            (models.Post.published) | (models.Post.owner_id == current_user_id)
        )

    if search:
        stmt = stmt.where(models.Post.title.contains(search))

    stmt = stmt.group_by(models.Post.id).order_by(desc(models.Post.created_at))
    return stmt


# -------------------- GET POSTS --------------------
@router.get("", response_model=List[schemas.PostVoted])
async def get_posts(
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
    limit: int = 10000,
    skip: int = 0,
    search: Optional[str] = "",
):
    stmt = get_posts_query(current_user.id, search)
    result = db.execute(stmt.limit(limit).offset(skip)).all()
    return [format_post_with_votes(row, current_user.id) for row in result]


@router.get("/me", response_model=List[schemas.PostVoted])
async def get_my_posts(
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
    limit: int = 10000,
    skip: int = 0,
    search: Optional[str] = "",
):
    stmt = get_posts_query(current_user.id, search, owner_only=True)
    result = db.execute(stmt.limit(limit).offset(skip)).all()
    return [format_post_with_votes(row, current_user.id) for row in result]


@router.get("/{id}", response_model=schemas.PostVoted)
async def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    stmt = get_posts_query(current_user.id).where(models.Post.id == id)
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    return format_post_with_votes(row, current_user.id)


# -------------------- CREATE POST --------------------
@router.post("", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# -------------------- UPDATE POST --------------------
@router.put("/{id}", response_model=schemas.Post)
async def update_post(
    id: int,
    post_data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post = db.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this post"
        )

    for field, value in post_data.model_dump().items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


# -------------------- DELETE POST --------------------
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post = db.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this post"
        )
    db.delete(post)
    db.commit()
    return {"detail": "Post deleted"}
