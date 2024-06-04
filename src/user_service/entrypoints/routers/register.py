from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..dependencies import validate_password, InvalidPassword, bus
from user_service.service_layer.handlers import EmailExisted
from ..schemas import RegisterRequest

router = APIRouter()


@router.post(
    "/register",
    tags=["users"],
    summary="Register a new user",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_201_CREATED: {
            "content": {
                "application/json": {
                    "example": {"message": "User successfully registered"}
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
        status.HTTP_409_CONFLICT: {
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
    },
)
async def register(body: RegisterRequest):
    try:
        validate_password(body.password)
    except InvalidPassword as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        cmd = commands.RegisterCommand(**body.model_dump())
        bus.handle(cmd)

    except EmailExisted as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return JSONResponse(
        content={"message": "User successfully registered"},
        status_code=status.HTTP_201_CREATED,
    )
