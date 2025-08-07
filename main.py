from fastapi import FastAPI
from .database.database import engine
from .models import models
from .routers import post, user

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "connected"}
