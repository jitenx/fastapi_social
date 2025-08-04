from sqlmodel import Field, SQLModel, create_engine, Session

SQLMODEL_DATABASE_URL = 'postgres://jitu:jitu@localhost/test'


class Posts(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, nullable=False)
    title: str | None = Field(default=None, nullable=False)
    content: str | None = Field(default=None, nullable=False)
    published: bool = Field(default=False, nullable=True)


engine = create_engine(SQLMODEL_DATABASE_URL)

SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
