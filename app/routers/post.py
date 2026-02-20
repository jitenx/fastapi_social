from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_
import app.models.models as models
import app.schemas.schemas as schemas
import app.auth.oauth2 as oauth2
from app.database.database import get_async_db

router = APIRouter(prefix="/posts", tags=["Posts"])


# -------------------- HELPERS --------------------


def format_post_with_votes(post_row):
    post, votes, user_voted_count = post_row
    return {
        "Post": post,
        "votes": votes,
        "user_voted": bool(user_voted_count),
    }


def check_post_owner(post, current_user):
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to perform this action",
        )


def get_posts_query(
    current_user_id: int,
    search: str = "",
    owner_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    # Base visibility
    if owner_only:
        visibility_filter = models.Post.owner_id == current_user_id
    else:
        visibility_filter = (models.Post.published) | (
            models.Post.owner_id == current_user_id
        )

    stmt = (
        select(
            models.Post,
            func.count(models.Vote.post_id).label("votes"),
            func.count(func.nullif(models.Vote.user_id != current_user_id, True)).label(
                "user_voted"
            ),
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .options(selectinload(models.Post.owner))
    )

    filters = [visibility_filter]

    # Search filter
    if search:
        search_term = f"%{search}%"
        filters.append(
            or_(
                models.Post.title.ilike(search_term),
                models.Post.content.ilike(search_term),
            )
        )

    # Date filter
    if start_date:
        filters.append(models.Post.created_at >= start_date)
    if end_date:
        filters.append(models.Post.created_at <= end_date)

    stmt = stmt.where(and_(*filters))

    return stmt.group_by(models.Post.id).order_by(desc(models.Post.created_at))


async def execute_post_query(
    db: AsyncSession,
    stmt,
    limit: int,
    skip: int,
):
    result = await db.execute(stmt.limit(limit).offset(skip))
    return result.all()


# -------------------- GET POSTS --------------------


@router.get("", response_model=List[schemas.PostVoted])
async def get_posts(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: Optional[str] = "",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    stmt = get_posts_query(
        current_user.id, search, start_date=start_date, end_date=end_date
    )
    posts = await execute_post_query(db, stmt, limit, skip)
    return [format_post_with_votes(row) for row in posts]


@router.get("/me", response_model=List[schemas.PostVoted])
async def get_my_posts(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
    limit: int = 50,
    skip: int = 0,
    search: Optional[str] = "",
):
    stmt = get_posts_query(current_user.id, search, owner_only=True)
    posts = await execute_post_query(db, stmt, limit, skip)
    return [format_post_with_votes(row) for row in posts]


@router.get("/{id}", response_model=schemas.PostVoted)
async def get_post(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    stmt = get_posts_query(current_user.id).where(models.Post.id == id)
    result = await db.execute(stmt)
    post_row = result.first()

    if not post_row:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    return format_post_with_votes(post_row)


# -------------------- CREATE POST --------------------


@router.post("", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: schemas.PostCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post_data.model_dump())
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


# -------------------- UPDATE POST --------------------


# -------------------- PATCH POST --------------------


@router.patch("/{id}", response_model=schemas.Post)
async def patch_post(
    id: int,
    post_data: schemas.PostUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    post = await db.get(models.Post, id)

    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    check_post_owner(post, current_user)

    update_data = post_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)

    return post


# -------------------- DELETE POST --------------------


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(oauth2.get_current_user),
):
    post = await db.get(models.Post, id)

    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    check_post_owner(post, current_user)

    await db.delete(post)
    await db.commit()
