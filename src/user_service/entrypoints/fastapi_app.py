from fastapi import FastAPI
from user_service import bootstrap
from .routers import user

app = FastAPI()
bus = bootstrap.bootstrap()

app.include_router(user.router, prefix="/user")
