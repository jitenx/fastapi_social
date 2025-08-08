from fastapi import FastAPI

from .routers import auth
from .database.database import engine
from .models import models
from .routers import post, user

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "connected"}
