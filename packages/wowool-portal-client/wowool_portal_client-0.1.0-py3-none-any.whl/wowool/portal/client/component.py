from dataclasses import dataclass


@dataclass
class Component:
    name: str
    type: str
    short_description: str | None = None
