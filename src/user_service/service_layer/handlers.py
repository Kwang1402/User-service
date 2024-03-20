from typing import List, Dict, Callable, Type
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work
from user_service.config import SECRET_KEY
import jwt
from flask_bcrypt import Bcrypt
import string
import random

bcrypt = Bcrypt()


class InvalidPassword(Exception):
    pass


class EmailExisted(Exception):
    pass


class IncorrectCredentials(Exception):
    pass


class UnathorizedAccess(Exception):
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


def validate_token(token, user_id):
    if not token:
        raise UnathorizedAccess("Authorization token missing")

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        authenticated_user_id = decoded_token.get("user_id")

        if authenticated_user_id != user_id:
            raise UnathorizedAccess("Unauthorized access to user account")

    except jwt.InvalidTokenError:
        raise UnathorizedAccess("Invalid token")


def random_valid_password(length=12):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation
    all_characters = lowercase_letters + uppercase_letters + digits + special_characters

    password = "".join(random.choice(all_characters) for _ in range(length - 4))
    password += random.choice(lowercase_letters)
    password += random.choice(uppercase_letters)
    password += random.choice(digits)
    password += random.choice(special_characters)

    return password


def register(
    cmd: commands.RegisterCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    if validate_password(cmd.password) is False:
        raise InvalidPassword(f"Invalid password '{cmd.password}'")
    
    with uow:
        user = uow.repo.get(models.User,email=cmd.email)
        if user:
            raise EmailExisted(f"Email {cmd.email} already existed")

        hashed_password = bcrypt.generate_password_hash(cmd.password).decode("utf-8")

        user = models.User(cmd.username, cmd.email, hashed_password)
        uow.repo.add(user)
        user.events.append(
            events.Registered(user.id, cmd.backup_email, cmd.gender, cmd.date_of_birth)
        )

        uow.commit()


def create_user_profile(
    event: events.Registered,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        profile = models.Profile(
            event.user_id, event.backup_email, event.gender, event.date_of_birth
        )
        uow.repo.add(profile)

        uow.commit()


def login(
    cmd: commands.LoginCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user is None or not bcrypt.check_password_hash(user.password, cmd.password):
            raise IncorrectCredentials("Incorrect email or password")

        token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")

        return token


def get_user(
    cmd: commands.GetUserCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    validate_token(cmd.token, cmd.user_id)
    with uow:
        user = uow.repo.get(models.User, id=cmd.user_id)
        return {"username": user.username, "email": user.email}


def reset_password(
    cmd: commands.ResetPasswordCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    new_password = random_valid_password()
    hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    with uow:
        user = uow.repo.get(models.User ,email=cmd.email)
        if user is None or user.username != cmd.username:
            raise IncorrectCredentials("Incorrect email or username")
        user.password = hashed_password

        uow.commit()

    return new_password


EVENT_HANDLERS = {
    events.Registered: [create_user_profile],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.RegisterCommand: register,
    commands.LoginCommand: login,
    commands.GetUserCommand: get_user,
    commands.ResetPasswordCommand: reset_password,
}  # type: Dict[Type[commands.Command], Callable]
