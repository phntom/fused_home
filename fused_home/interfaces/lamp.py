from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from interfaces.appliance import Appliance


@dataclass
class Lamp(Appliance):
    @dataclass
    class Transition:
        class Effect(Enum):
            SMOOTH = "smooth"
            SUDDEN = "sudden"

        effect: Effect = field(default=Effect.SMOOTH)
        duration: Optional[int] = field(default=1000)

    power: Optional[bool] = field(default=None)  # percent * 100
    brightness: Optional[int] = field(default=None)  # percent * 100
    fw_ver: Optional[int] = field(default=None)
    transition: Transition = field(default=Transition())

    read_only: bool = field(default=False)

    # TODO: support cron, scene, cf, default, music


@dataclass
class ColorLamp(Lamp):
    rgb: Optional[int] = field(default=None)
    hue: Optional[int] = field(default=None)
    sat: Optional[int] = field(default=None)
    color_mode: Optional[int] = field(default=None)
    ct: Optional[int] = field(default=None)
