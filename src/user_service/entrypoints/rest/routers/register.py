from fastapi import APIRouter, HTTPException, status

from ..dependencies import validate_password, InvalidPassword
from user_service.domains import commands
from user_service import bootstrap
from user_service.domains import models
from user_service.service_layer.handlers.command import EmailExisted
from user_service.entrypoints.schemas import register_schemas
from user_service import views

bus = bootstrap.bootstrap()

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=register_schemas.RegisterResponse,
)
async def register(cmd: commands.RegisterCommand):
    try:
        validate_password(cmd.password)
    except InvalidPassword as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        cmd = commands.RegisterCommand(**cmd.model_dump())
        bus.handle(cmd)

    except EmailExisted as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    # users = views.fetch_models_from_database(
    #     model_type=models.User, uow=bus.uow, message_id=cmd._id
    # )
    # user = users[0]
    # print(user)
    # profiles = views.fetch_models_from_database(
    #     model_type=models.Profile, uow=bus.uow, user_id=user.id
    # )
    # profile = profiles[0]

    with bus.uow:
        users = bus.uow.repo.get(models.User, message_id=cmd._id)
        user = users[0]
        profiles = bus.uow.repo.get(models.Profile, user_id=user.id)
        profile = profiles[0]

        register_response = register_schemas.RegisterSchema(
            id = user.id,
            created_time=user.created_time,
            updated_time=user.updated_time,
            username=user.username,
            email=user.email,
            password=user.password,
            first_name=profile.first_name,
            last_name=profile.last_name,
            backup_email=profile.backup_email,
            gender=profile.gender,
            date_of_birth=profile.date_of_birth
        )
        
        return register_schemas.RegisterResponse(register=register_response)
