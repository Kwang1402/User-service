from fastapi import FastAPI
from .routers import register, login, user, reset_password

app = FastAPI()

app.include_router(register.router)
app.include_router(login.router)
app.include_router(user.router)
app.include_router(reset_password.router)
