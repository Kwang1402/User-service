import fastapi

from user_service import bootstrap
from user_service.domains import commands
from user_service.service_layer.handlers.command import IncorrectCredentials

bus = bootstrap.bootstrap()

router = fastapi.APIRouter()


@router.post(
    "/reset-password",
    status_code=fastapi.status.HTTP_200_OK,
)
async def reset_password(cmd: commands.ResetPasswordCommand):
    try:
        bus.handle(cmd)

    except IncorrectCredentials as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e)
        )

    return fastapi.status.HTTP_200_OK
