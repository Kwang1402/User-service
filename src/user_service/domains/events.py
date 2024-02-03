from dataclasses import dataclass


class Event:
    pass


@dataclass
class Registered(Event):
    id: str
