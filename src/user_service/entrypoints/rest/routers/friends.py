from typing import Annotated, List

from fastapi import Depends, APIRouter, status

from .. import dependencies
from user_service import bootstrap
from user_service.domains import commands, models
from user_service.entrypoints.schemas import (
    friend_schemas,
)  # from user_service.entrypoints import schemas
from user_service import views

bus = bootstrap.bootstrap()

router = APIRouter()


# API conventions: https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design
@router.post(
    "/friend-request",
    status_code=status.HTTP_201_CREATED,
    response_model=friend_schemas.FriendRequestResponse,
)
async def friend_request(cmd: commands.FriendRequestCommand):
    bus.handle(cmd)

    friend_request_response = views.fetch_models_from_database(
        model_type=models.FriendRequest, uow=bus.uow, message_id=cmd._id
    )[0]

    return friend_schemas.FriendRequestResponse(friend_request=friend_request_response)


@router.get(
    "/friend-requests",
    status_code=status.HTTP_200_OK,
    response_model=List[friend_schemas.FriendRequestSchema],
)
async def get_friend_requests(
    current_user: Annotated[models.User, Depends(dependencies.get_current_unlock_user)]
):
    friend_requests = views.fetch_models_from_database(
        model_type=models.FriendRequest,
        uow=bus.uow,
        receiver_id=current_user.id,
        status="Pending",
    )

    # create a seperate schema
    friend_requests_repsonse = (
        [
            friend_schemas.FriendRequestResponse(friend_request=friend_request)
            for friend_request in friend_requests
        ]
        if friend_requests
        else []
    )

    return friend_requests_repsonse


# /friend-requests/{id}/accept
# POST
@router.patch(
    "/accept-friend-request",
    status_code=status.HTTP_200_OK,
    response_model=friend_schemas.AcceptFriendRequestResponse,
)
async def accept_friend_request(cmd: commands.AcceptFriendRequestCommand):
    bus.handle(cmd)

    accept_friend_request_response = views.fetch_models_from_database(
        model_type=models.FriendRequest, uow=bus.uow, id=cmd.friend_request.id
    )[0]

    return friend_schemas.AcceptFriendRequestResponse(
        accept_friend_request=accept_friend_request_response
    )


#
# DELETE
@router.patch(
    "/decline-friend-request",
    status_code=status.HTTP_200_OK,
    response_model=friend_schemas.DeclineFriendRequestResponse,
)
async def decline_friend_request(cmd: commands.DeclineFriendRequestCommand):
    bus.handle(cmd)

    decline_friend_request_response = views.fetch_models_from_database(
        model_type=models.FriendRequest, uow=bus.uow, id=cmd.friend_request.id
    )[0]

    return friend_schemas.DeclineFriendRequestResponse(
        decline_friend_request=decline_friend_request_response
    )
