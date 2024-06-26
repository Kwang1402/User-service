import fastapi
from user_service.entrypoints.rest.routers import (
    register,
    login,
    user,
    reset_password,
    friends,
)


app = fastapi.FastAPI(docs_url=None, redoc_url="/docs")

app.include_router(register.router)
app.include_router(login.router)
app.include_router(user.router)
app.include_router(reset_password.router)
app.include_router(friends.router)
