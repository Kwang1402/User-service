from typing import List, Dict, Callable, Type
import string
import random
from datetime import datetime
from user_service.domains import commands, events, models
from user_service.service_layer import unit_of_work
from passlib.context import CryptContext
import pyotp

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
        user = uow.repo.get(models.User, email=cmd.email)
        if user:
            raise EmailExisted(f"Email {cmd.email} already existed")
        user = uow.repo.get(models.User, username=cmd.username)
        if user:
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


def enable_two_factor_auth(
    cmd: commands.EnableTwoFactorAuthCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, id=cmd.user_id)
        otp_code = pyotp.TOTP(user.secret_token).now()
        email_address = f"mock_emails/{user.email}.txt"

    with open(email_address, "a") as file:
        file.write(f"{otp_code}\n")


def verify_enable_two_factor_auth(
    cmd: commands.EnableTwoFactorAuthCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, id=cmd.user_id)

        if not pyotp.TOTP(user.secret_token).verify(cmd.otp_code):
            raise InvalidOTP("Invalid OTP code")

        user.enable_two_factor_auth()

        uow.commit()


def login(
    cmd: commands.LoginCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)

        if user is None or not pwd_context.verify(cmd.password, user.password):
            raise IncorrectCredentials("Incorrect email or password")

        user.message_id = cmd._id

        if not user.two_factor_auth_enabled:
            raise TwoFactorAuthNotEnabled(user.id)

        uow.commit()


def reset_password(
    cmd: commands.ResetPasswordCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        user = uow.repo.get(models.User, email=cmd.email)
        if user is None or user.username != cmd.username:
            raise IncorrectCredentials("Incorrect email or username")

        new_password = random_valid_password()
        new_hashed_password = pwd_context.hash(new_password)
        user.change_password(new_hashed_password)
        email_address = f"mock_emails/{user.email}.txt"

        uow.commit()

    with open(email_address, "a") as file:
        file.write(f"{new_password}\n")


def add_friend(
    cmd: commands.AddFriendCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend_request = models.FriendRequest(cmd._id, cmd.sender_id, cmd.receiver_id)
        uow.repo.add(friend_request)

        uow.commit()


def accept_friend_request(
    cmd: commands.AcceptFriendRequestCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend_request = uow.repo.get(models.FriendRequest, id=cmd.friend_request_id)
        friend_request.status = "Accepted"
        friend_request.updated_time = datetime.now()

        friend_request.events.append(
            events.AcceptedFriendRequestEvent(sender_id=friend_request.sender_id, receiver_id=friend_request.receiver_id)
        )

        uow.commit()


def decline_friend_request(
    cmd: commands.DeclineFriendRequestCommand,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend_request = uow.repo.get(models.FriendRequest, id=cmd.friend_request_id)
        friend_request.status = "Declined"
        friend_request.updated_time = datetime.now()

        uow.commit()

def add_to_friend_list(
    event: events.AcceptedFriendRequestEvent,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        friend = models.Friend(event._id, event.sender_id, event.receiver_id)
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

COMMAND_HANDLERS = {
    commands.RegisterCommand: register,
    commands.EnableTwoFactorAuthCommand: enable_two_factor_auth,
    commands.VerifyEnableTwoFactorAuthCommand: verify_enable_two_factor_auth,
    commands.LoginCommand: login,
    commands.ResetPasswordCommand: reset_password,
    commands.AddFriendCommand: add_friend,
    commands.AcceptFriendRequestCommand: accept_friend_request,
}  # type: Dict[Type[commands.Command], Callable]
