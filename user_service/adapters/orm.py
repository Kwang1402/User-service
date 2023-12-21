from sqlalchemy import (
    Table,
    Column,
    String,
    Uuid,
    Integer,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import registry, relationship

from user_service.domains import models

mapper_registry = registry()

users = Table(
    "users",
    mapper_registry.metadata,
    Column("id", Uuid, primary_key=True),
    Column("username", String(255)),
    Column("password", String(255)),
    Column("locked", Boolean),
    Column("created_time", DateTime),
    Column("updated_time", DateTime),
)

profiles = Table(
    "profiles",
    mapper_registry.metadata,
    Column("id", Uuid, primary_key=True),
    Column("user_id", Uuid, ForeignKey("users.id"), nullable=False),
    Column("backup_email", String(255)),
    Column("gender", String(10)),
    Column("date_of_birth", Date),
)

event_types = Table(
    "event_types",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(50)),
)

events = Table(
    "events",
    mapper_registry.metadata,
    Column("id", Uuid, primary_key=True),
    Column("type_id", Integer, ForeignKey("event_types.id")),
    Column("created_by", Uuid, ForeignKey("users.id"), nullable=False),
)

trusted_devices = Table(
    "trusted_devices",
    mapper_registry.metadata,
    Column("id", Uuid, primary_key=True),
    Column("users_id", Uuid, ForeignKey("users.id"), nullable=False),
)


def start_mappers():
    users_mapper = mapper_registry.map_imperatively(
        models.User,
        users,
        properties={
            "profiles": relationship(
                models.Profile, backref="users", order_by=profiles.c.id
            ),
            "events": relationship(models.Event, backref="users", order_by=events.c.id),
            "trusted_devices": relationship(
                models.TrustedDevice, backref="users", order_by=trusted_devices.c.id
            ),
        },
    )
    profiles_mapper = mapper_registry.map_imperatively(models.Profile, profiles)
    event_types_mapper = mapper_registry.map_imperatively(
        models.EventType,
        event_types,
        properties={
            "events": relationship(
                models.Event, backref="event_types", order_by=events.c.id
            )
        },
    )
    events_mapper = mapper_registry.map_imperatively(models.Event, events)
    trusted_devices_mapper = mapper_registry.map_imperatively(
        models.TrustedDevice, trusted_devices
    )
