from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from user_service.domains import commands
from ..fastapi_app import bus
from ..dependencies import validate_token, UnauthorizedAccess

router = APIRouter()


@router.get("user/{user_id}")
async def get_user(user_id: str, request: Request):
    authorization = request.headers.get("Authorization", "")
    try:
        token = authorization.replace("Bearer", "")
        validate_token(token, user_id)
    except UnauthorizedAccess as e:
        raise HTTPException(status_code=401, detail=str(e))        

    cmd = commands.GetUserCommand(user_id, token)
    results = bus.handle(cmd)
    user = results[0]
    
    return JSONResponse(content={"user": user}, status_code=200)
