from typing import Dict, Callable, Type
import string
import random
from datetime import datetime
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work
from passlib.context import CryptContext
import pyotp
from icecream import ic

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsernameExisted(Exception):
    pass


class EmailExisted(Exception):
    pass


class IncorrectCredentials(Exception):
    pass


class TwoFactorAuthNotEnabled(Exception):
    pass


class InvalidOTP(Exception):
    pass


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
    with uow:
        users = uow.repo.get(models.User, email=cmd.email)
        if users:
            raise EmailExisted(f"Email {cmd.email} already existed")
        users = uow.repo.get(models.User, username=cmd.username)
        if users:
            raise UsernameExisted(f"Username {cmd.username} already existed")

        hashed_password = pwd_context.hash(cmd.password)
        secret_token = pyotp.random_base32()

        user = models.User(
            cmd._id, cmd.username, cmd.email, hashed_password, secret_token
        )
        uow.repo.add(user)

        user.events.append(
            events.RegisteredEvent(
                user_id=user.id,
                first_name=cmd.first_name,
                last_name=cmd.last_name,
                backup_email=cmd.backup_email,
                gender=cmd.gender,
                date_of_birth=cmd.date_of_birth,
            )
        )

        uow.commit()


def setup_two_factor_auth(
    cmd: commands.SetupTwoFactorAuthCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        users = uow.repo.get(models.User, id=cmd.user_id)
        user = users[0]
        otp_code = pyotp.TOTP(user.secret_token).now()
        email_address = f"mock_emails/{user.email}.txt"

    with open(email_address, "a") as file:
        file.write(f"{otp_code}\n")


def verify_two_factor_auth(
    cmd: commands.VerifyTwoFactorAuthCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        users = uow.repo.get(models.User, id=cmd.user_id)
        user = users[0]

        if not pyotp.TOTP(user.secret_token).verify(cmd.otp_code):
            raise InvalidOTP("Invalid OTP code")

        user.enable_two_factor_auth()

        uow.commit()


def login(
    cmd: commands.LoginCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        users = uow.repo.get(models.User, username=cmd.username)

        if not users:
            users = uow.repo.get(models.User, email=cmd.username)

        if not users:
            raise IncorrectCredentials("Incorrect username or password")

        user = users[0]
        if not pwd_context.verify(cmd.password, user.password):
            raise IncorrectCredentials("Incorrect username or password")

        if not user.two_factor_auth_enabled:
            raise TwoFactorAuthNotEnabled(user.id)


def reset_password(
    cmd: commands.ResetPasswordCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        users = uow.repo.get(models.User, email=cmd.email)
        if not users:
            raise IncorrectCredentials("Incorrect email or username")

        user = users[0]
        if user.username != cmd.username:
            raise IncorrectCredentials("Incorrect email or username")

        new_password = random_valid_password()
        new_hashed_password = pwd_context.hash(new_password)
        user.change_password(new_hashed_password)
        email_address = f"mock_emails/{user.email}.txt"

        uow.commit()

    with open(email_address, "a") as file:
        file.write(f"{new_password}\n")


def create_friend_request(
    cmd: commands.FriendRequestCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend_request = models.FriendRequest(message_id=cmd._id, **cmd.model_dump())
        uow.repo.add(friend_request)

        uow.commit()


def accept_friend_request(
    cmd: commands.AcceptFriendRequestCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend_requests = uow.repo.get(models.FriendRequest, id=cmd.friend_request.id)

        friend_request = friend_requests[0]

        friend_request.events.append(
            events.AcceptedFriendRequestEvent(friend_request_id=cmd.friend_request.id)
        )

        uow.commit()


def decline_friend_request(
    cmd: commands.DeclineFriendRequestCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend_requests = uow.repo.get(models.FriendRequest, id=cmd.friend_request_id)

        friend_request = friend_requests[0]

        uow.repo.remove(friend_request)

        uow.commit()


COMMAND_HANDLERS = {
    commands.RegisterCommand: register,
    commands.SetupTwoFactorAuthCommand: setup_two_factor_auth,
    commands.VerifyTwoFactorAuthCommand: verify_two_factor_auth,
    commands.LoginCommand: login,
    commands.ResetPasswordCommand: reset_password,
    commands.FriendRequestCommand: create_friend_request,
    commands.AcceptFriendRequestCommand: accept_friend_request,
}  # type: Dict[Type[commands.Command], Callable]
