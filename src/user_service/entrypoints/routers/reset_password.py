from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..dependencies import bus
from user_service.entrypoints import schemas
from user_service.service_layer.handlers import IncorrectCredentials

router = APIRouter()


@router.post(
    "/reset-password",
    tags=["users"],
    summary="Reset user's password",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {"example": {"message": "string"}}}
        },
        status.HTTP_400_BAD_REQUEST: {
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
    },
)
async def reset_password(body: schemas.ResetPasswordSchema):
    try:
        cmd = commands.ResetPasswordCommand(**body.model_dump())
        bus.handle(cmd)

    except IncorrectCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return JSONResponse(
        content={"message": "Password successfully reset"},
        status_code=status.HTTP_200_OK,
    )
