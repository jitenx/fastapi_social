from sqlalchemy import Boolean, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    posts: Mapped[list["Post"]] = relationship(
        "Post", back_populates="owner", cascade="all, delete-orphan"
    )
    votes: Mapped[list["Vote"]] = relationship(
        "Vote", back_populates="user", cascade="all, delete-orphan"
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="TRUE"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="posts")
    votes: Mapped[list["Vote"]] = relationship(
        "Vote", back_populates="post", cascade="all, delete-orphan"
    )


class Vote(Base):
    __tablename__ = "votes"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="votes")
    post: Mapped["Post"] = relationship("Post", back_populates="votes")
