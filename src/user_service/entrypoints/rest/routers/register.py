import fastapi

from .. import dependencies
from user_service.domains import commands
from user_service import bootstrap
from user_service.service_layer.handlers import command

bus = bootstrap.bootstrap()

router = fastapi.APIRouter()


@router.post(
    "/register",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
async def register(cmd: commands.RegisterCommand):
    try:
        dependencies.validate_password(cmd.password)
    except dependencies.InvalidPassword as e:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        cmd = commands.RegisterCommand(**cmd.model_dump())
        bus.handle(cmd)

    except (command.EmailExisted, command.UsernameExisted) as e:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT, detail=str(e))

    return fastapi.status.HTTP_204_NO_CONTENT
