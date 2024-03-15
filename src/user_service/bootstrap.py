import inspect
from user_service.adapters import orm
from user_service.service_layer import handlers, message_bus, unit_of_work
import typing as t

def bootstrap(
    start_orm: bool = True,
    uow: t.Type[unit_of_work.AbstractUnitOfWork] = unit_of_work.SqlAlchemyUnitOfWork
) -> message_bus.MessageBus:
    if start_orm:
        orm.start_mappers()

    if isinstance(uow, type):
        uow = uow()
        
    dependencies = {"uow": uow}
    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in event_handlers
        ]
        for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    return message_bus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }
    return lambda message: handler(message, **deps)
