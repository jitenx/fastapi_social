from typing import Annotated
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import Depends, FastAPI, HTTPException, status

app = FastAPI()

SQLMODEL_DATABASE_URL = 'postgresql://jitu:jitu@localhost:5432/test'


class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    title: str | None = Field(default=None, nullable=False)
    content: str | None = Field(default=None, nullable=False)
    published: bool = Field(default=False, nullable=True)


engine = create_engine(SQLMODEL_DATABASE_URL)

SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/posts", response_model=list[Post])
def get_posts(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    post = session.exec(select(Post).offset(skip).limit(limit)).all()
    return post


@app.get("/")
def root():
    return {"message": "Hello"}


@app.post("/createposts", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(post: Post, session: Session = Depends(get_session)):
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@app.get("/posts/{id}", response_model=Post)
def get_post(id: int, session: Session = Depends(get_session)):
    post = session.get(Post, id)
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: Session = Depends(get_session)):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    session.delete(post)
    session.commit()
    return post


@app.put("/posts/{id}", response_model=Post, status_code=status.HTTP_200_OK)
def update_post(id: int, post_data: Post, session: Session = Depends(get_session)):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} is not found")
    for field, value in post_data.model_dump().items():
        setattr(post, field, value)
    session.commit()
    session.refresh(post)
    return post
