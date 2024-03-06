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
    DateTime,
    ForeignKey,
    event,
)
from sqlalchemy.orm import registry, relationship, clear_mappers


from user_service.domains import models
from user_service import config

logger = logging.getLogger(__name__)

mapper_registry = registry()
metadata = MetaData()
engine = create_engine(config.get_sqlite_uri())

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
    mapper_registry.metadata.create_all(bind=engine)


@event.listens_for(models.User, "load")
def receive_load(user, _):
    user.events = []
