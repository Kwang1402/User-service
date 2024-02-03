import logging
from sqlalchemy import (
    Table,
    MetaData,
    Column,
    String,
    Integer,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    event,
)
from sqlalchemy.orm import registry, relationship

from user_service.domains import models

logger = logging.getLogger(__name__)

mapper_registry = registry()
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("username", String(255)),
    Column("email", String(255)),
    Column("password", String(255)),
    Column("locked", Boolean),
    Column("created_time", DateTime),
    Column("updated_time", DateTime),
)

profiles = Table(
    "profiles",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("user_id", String(255), ForeignKey("users.id"), nullable=False),
    Column("backup_email", String(255)),
    Column("gender", String(10)),
    Column("date_of_birth", Date),
)


def start_mappers():
    logger.info("Starting mappers")
    mapper_registry.map_imperatively(
        models.User,
        users,
        properties={
            "profile": relationship(models.Profile, backref="users", uselist=False)
        },
    )
    mapper_registry.map_imperatively(models.Profile, profiles)


@event.listens_for(models.User, "load")
def receive_load(user, _):
    user.events = []
