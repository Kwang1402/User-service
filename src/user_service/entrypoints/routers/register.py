from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..dependencies import validate_password, InvalidPassword, bus
from user_service.service_layer.handlers import EmailExisted

router = APIRouter()


@router.post("/register")
async def register(request: Request):
    try:
        body = await request.json()
        validate_password(body["password"])
    except InvalidPassword as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        cmd = commands.RegisterCommand(**body)
        bus.handle(cmd)

    except EmailExisted as e:
        raise HTTPException(status_code=409, detail=str(e))

    return JSONResponse(
        content={"message": "User successfully registered"}, status_code=201
    )
