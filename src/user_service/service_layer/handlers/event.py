from typing import List, Dict, Callable, Type
from datetime import datetime
from user_service.domains import events, models
from user_service.service_layer import unit_of_work


def create_user_profile(
    event: events.RegisteredEvent,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        profile = models.Profile(
            message_id=event._id,
            **event.model_dump(),
        )
        uow.repo.add(profile)

        uow.commit()


def add_to_friend_list(
    event: events.AcceptedFriendRequestEvent,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend_request = uow.repo.get(models.FriendRequest, id=event.friend_request_id)[0]
        sender_id = friend_request.sender_id
        receiver_id = friend_request.receiver_id

        friend = models.Friend(event._id, sender_id=sender_id, receiver_id=receiver_id)
        uow.repo.add(friend)

        sender_profile = uow.repo.get(models.Profile, user_id=sender_id)[0]
        sender_profile.friends += 1
        sender_profile.updated_time = datetime.now()

        receiver_profile = uow.repo.get(models.Profile, user_id=receiver_id)[0]
        receiver_profile.friends += 1
        receiver_profile.updated_time = datetime.now()

        uow.commit()


def remove_friend_request(
    event: events.AcceptedFriendRequestEvent, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        friend_request = uow.repo.get(models.FriendRequest, id=event.friend_request_id)[0]
        uow.repo.remove(friend_request)

        uow.commit()


EVENT_HANDLERS = {
    events.RegisteredEvent: [create_user_profile],
    events.AcceptedFriendRequestEvent: [add_to_friend_list, remove_friend_request],
}  # type: Dict[Type[events.Event], List[Callable]]
