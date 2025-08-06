from typing import Any, List, Optional
from fastapi import Body, FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy import TIMESTAMP
from .database import engine, get_db
from sqlalchemy.orm import Session
from . import models
from . import schemas
models.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello"}


@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    return post


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,  db: Session = Depends(get_db)):
    post = db.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    db.delete(post)
    db.commit()
    return post


@app.put("/posts/{id}", response_model=schemas.Post, status_code=status.HTTP_200_OK)
def update_post(id: int, post_data: schemas.PostCreate, db: Session = Depends(get_db)):
    post = db.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    for field, value in post_data.model_dump().items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post
