from fastapi import APIRouter, HTTPException, status

from user_service import bootstrap
from user_service.domains import commands
from user_service.entrypoints.schemas import reset_password_schemas
from user_service.service_layer.handlers.command import IncorrectCredentials

bus = bootstrap.bootstrap()

router = APIRouter()


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    response_model=reset_password_schemas.ResetPasswordResponse,
)
async def reset_password(cmd: commands.ResetPasswordCommand):
    try:
        bus.handle(cmd)

    except IncorrectCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    reset_password_response = reset_password_schemas.ResetPasswordSchema(
        *cmd.body_dump(), message="Password reset"
    )

    return reset_password_schemas.ResetPasswordResponse(
        reset_password=reset_password_response
    )
