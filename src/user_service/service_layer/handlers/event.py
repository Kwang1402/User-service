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
        friend = models.Friend(event._id, **event.model_dump())
        uow.repo.add(friend)

        sender_profile = uow.repo.get(models.Profile, user_id=event.sender_id)
        sender_profile.friends += 1
        sender_profile.updated_time = datetime.now()

        receiver_profile = uow.repo.get(models.Profile, user_id=event.receiver_id)
        receiver_profile.friends += 1
        receiver_profile.updated_time = datetime.now()

        uow.commit()


EVENT_HANDLERS = {
    events.RegisteredEvent: [create_user_profile],
    events.AcceptedFriendRequestEvent: [add_to_friend_list],
}  # type: Dict[Type[events.Event], List[Callable]]
