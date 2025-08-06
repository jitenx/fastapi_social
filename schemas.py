from datetime import datetime
from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime


class UserCreate(BaseModel):
    email: str
    password: str


class User(BaseModel):
    email: str
