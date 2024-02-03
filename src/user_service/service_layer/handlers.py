import logging
from typing import List, Dict, Callable, Type
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work

import uuid
import string


class InvalidPassword(Exception):
    pass


class EmailExisted(Exception):
    pass


def validate_password(password: str) -> bool:
    # Minimum length
    if len(password) < 8:
        return False

    # No spaces
    if " " in password:
        return False

    # At least one digit
    if not any(c.isdigit() for c in password):
        return False

    # At least one special character
    if not any(c in string.punctuation for c in password):
        return False

    return True


def register(
    cmd: commands.Register,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        if validate_password(cmd.password) is False:
            raise InvalidPassword(f"Invalid password '{cmd.password}'")
        user = uow.users.get_by_email(email=cmd.email)
        if user:
            raise EmailExisted(f"Email {cmd.email} already existed")
        # user_id = str(uuid.uuid4())
        # profile_id = str(uuid.uuid4())
        uow.users.add(
            models.User(
                cmd.username,
                cmd.email,
                cmd.password,
                models.Profile(
                    cmd.backup_email,
                    cmd.gender,
                    cmd.date_of_birth,
                ),
            )
        )
        uow.commit()


def registered(
    event: events.Registered,
):
    print(f"Registed user {event.id}")


EVENT_HANDLERS = {
    events.Registered: [registered],
}

COMMAND_HANDLERS = {
    commands.Register: register,
}
