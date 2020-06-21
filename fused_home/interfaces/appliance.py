from dataclasses import dataclass, field
from typing import Optional

from home.room import Room


@dataclass
class Appliance:
    internal_id: str
    friendly_name: str
    home: str
    read_only: bool = field(default=True)
    room: Optional[Room] = field(default=None)

    @property
    def id(self):
        return '{}-{}-{}'.format(self.home, self.__class__.__name__, self.internal_id)

    def _on_change(self, old_state: dict, new_state: dict):
        raise NotImplemented

    def expand(self):
        yield self


@dataclass
class OnBattery(Appliance):
    voltage: Optional[int] = field(default=None)
