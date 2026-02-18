from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


class PasswordMixin(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain a number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain a special character")

        return value


# -------------------- USER SCHEMAS --------------------
class UserCreate(PasswordMixin):
    first_name: str
    last_name: str
    email: EmailStr
    # phone_number: Optional[str] = None
    # address: Optional[str] = None


class UserPublic(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserOut(User):
    # phone_number: Optional[str] = None
    # address: Optional[str] = None
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserDelete(BaseModel):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    current_password: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------- POST SCHEMAS --------------------
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

    class Config:
        from_attributes = True


class PostVoted(BaseModel):
    Post: Post
    votes: int
    user_voted: bool

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

    class Config:
        from_attributes = True


# -------------------- AUTH / VOTE SCHEMAS --------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: bool  # True = vote, False = remove vote
