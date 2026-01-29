from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    # phone_number: str
    # address: str


class UserPublic(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    id: int
    created_at: datetime

    class ConfigDict:
        orm_mode = True


class UserOut(User):
    # phone_number: str
    # address: str

    class ConfigDict:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserPublic

    class ConfigDict:
        orm_mode = True


class PostVoted(BaseModel):
    Post: Post
    votes: int
    user_voted: bool

    class ConfigDict:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: bool


class UserDelete(BaseModel):
    password: str
