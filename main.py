from fastapi import FastAPI


from .database.database import engine
from .models import models
from .routers import post, user, auth, vote
from .utils.config import settings

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "connected"}
