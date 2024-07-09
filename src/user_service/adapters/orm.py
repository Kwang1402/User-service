import logging

from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    Column,
    String,
    Integer,
    Boolean,
    Date,
    TIMESTAMP,
    ForeignKey,
    event,
)
from sqlalchemy.orm import registry, relationship

from user_service.domains import models
from user_service import config

logger = logging.getLogger(__name__)

mapper_registry = registry()
metadata = MetaData()
engine = create_engine(config.get_mysql_uri())

users = Table(
    "users",
    metadata,
    Column("message_id", String(255)),
    Column("id", String(255), primary_key=True),
    Column("username", String(255), unique=True),
    Column("email", String(255), unique=True),
    Column("password", String(255)),
    Column("secret_token", String(255), unique=True),
    Column("two_factor_auth_enabled", Boolean),
    Column("locked", Boolean),
    Column("created_time", TIMESTAMP),
    Column("updated_time", TIMESTAMP),
)

profiles = Table(
    "profiles",
    metadata,
    Column("message_id", String(255)),
    Column("id", String(255), primary_key=True),
    Column("user_id", String(255), ForeignKey("users.id"), nullable=False),
    Column("first_name", String(255)),
    Column("last_name", String(255)),
    Column("backup_email", String(255)),
    Column("gender", String(255)),
    Column("date_of_birth", Date),
    Column("followers", Integer),
    Column("friends", Integer),
    Column("created_time", TIMESTAMP),
    Column("updated_time", TIMESTAMP),
)

friend_requests = Table(
    "friend_requests",
    metadata,
    Column("message_id", String(255)),
    Column("id", String(255), primary_key=True),
    Column("sender_id", String(255)),
    Column("receiver_id", String(255)),
    Column("created_time", TIMESTAMP),
    Column("updated_time", TIMESTAMP),
)

friends = Table(
    "friends",
    metadata,
    Column("message_id", String(255)),
    Column("id", String(255), primary_key=True),
    Column("sender_id", String(255)),
    Column("receiver_id", String(255)),
    Column("created_time", TIMESTAMP),
    Column("updated_time", TIMESTAMP),
)

_mappers_initialized = False


def start_mappers():
    global _mappers_initialized
    if _mappers_initialized:
        return

    logger.info("Starting mappers")
    mapper_registry.map_imperatively(
        models.User,
        users,
        properties={
            "profile": relationship(models.Profile, backref="users", uselist=False)
        },
    )
    mapper_registry.map_imperatively(models.Profile, profiles)
    mapper_registry.map_imperatively(models.FriendRequest, friend_requests)
    mapper_registry.map_imperatively(models.Friend, friends)
    mapper_registry.metadata.create_all(bind=engine)

    _mappers_initialized = True


@event.listens_for(models.User, "load")
def receive_load(user, _):
    user.events = []
