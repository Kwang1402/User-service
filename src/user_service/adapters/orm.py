import logging
from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    Column,
    String,
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
engine = create_engine(config.get_sqlite_uri())

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("username", String),
    Column("email", String, unique=True),
    Column("password", String),
    Column("secret_token", String, unique=True),
    Column("two_factor_auth_enabled", Boolean),
    Column("locked", Boolean),
    Column("created_time", TIMESTAMP),
    Column("updated_time", TIMESTAMP),
)

profiles = Table(
    "profiles",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), nullable=False),
    Column("backup_email", String),
    Column("gender", String),
    Column("date_of_birth", Date),
    Column("created_time", TIMESTAMP),
    Column("updated_time", TIMESTAMP),
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
    mapper_registry.metadata.create_all(bind=engine)


@event.listens_for(models.User, "load")
def receive_load(user, _):
    user.events = []
