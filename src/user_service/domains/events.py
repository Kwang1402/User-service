import dataclasses


class Event:
    pass


@dataclasses.dataclass
class Registered(Event):
    user_id: str
