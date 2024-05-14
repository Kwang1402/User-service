from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..dependencies import bus
from user_service.service_layer.handlers import IncorrectCredentials

router = APIRouter()


@router.post("/reset-password")
async def reset_password(request: Request):
    try:
        body = await request.json()
        cmd = commands.ResetPasswordCommand(**body)
        results = bus.handle(cmd)
        new_password = results[0]

    except IncorrectCredentials as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"new_password": new_password}, status_code=200)
