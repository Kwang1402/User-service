from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..dependencies import bus
from user_service.service_layer.handlers import (
    IncorrectCredentials,
    TwoFactorAuthNotEnabled,
)

router = APIRouter()


@router.post("/login")
async def login(request: Request):
    try:
        body = await request.json()
        cmd = commands.LoginCommand(**body)
        results = bus.handle(cmd)
        user_id, token = results[0]

    except (IncorrectCredentials, TwoFactorAuthNotEnabled) as e:
        raise HTTPException(status_code=401, detail=str(e))

    return JSONResponse(content={"user_id": user_id, "token": token}, status_code=200)
