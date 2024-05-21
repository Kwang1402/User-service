from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..dependencies import bus
from ..schemas import ResetPasswordRequest
from user_service.service_layer.handlers import IncorrectCredentials

router = APIRouter()


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    try:
        cmd = commands.ResetPasswordCommand(**body.model_dump())
        results = bus.handle(cmd)
        new_password = results[0]

    except IncorrectCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return JSONResponse(
        content={"new_password": new_password}, status_code=status.HTTP_200_OK
    )
