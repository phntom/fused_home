from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from interfaces.appliance import Appliance


class Sensor(Appliance):
    pass


@dataclass
class Motion(Sensor):
    last_detection: Optional[datetime] = field(default=None)


@dataclass
class Switch(Sensor):
    class Interaction(Enum):
        CLICK = "click"
        DOUBLE_CLICK = "double_click"
        LONG_CLICK = "long_click"

    last_interaction: Optional[datetime] = field(default=None)
    interaction: Optional[Interaction] = field(default=None)


@dataclass
class Thermometer(Sensor):
    temperature: Optional[int] = field(default=None)
    humidity: Optional[int] = field(default=None)


@dataclass
class Magnet(Sensor):
    class Status(Enum):
        CLOSE = "close"
        OPEN = "open"

    status: Optional[Status] = field(default=None)


@dataclass
class Lux(Sensor):
    class LuxLevel(Enum):
        DARK = "dark"
        DIM = "dim"
        NORMAL = "normal"
        BRIGHT = "bright"

        @classmethod
        def from_percentage(cls, percentage):
            if percentage < 1500:
                return cls.DARK
            if percentage < 3500:
                return cls.DIM
            if percentage < 8000:
                return cls.NORMAL
            if percentage < 10000:
                return cls.BRIGHT
            return None

    level: Optional[LuxLevel] = field(default=None)


@dataclass
class AirQuality(Sensor):
    class Quality(Enum):
        BAD = "bad"
        GOOD = "good"
        EXCELLENT = "excellent"

    quality: Optional[Quality] = field(default=None)


@dataclass
class Noise(Sensor):
    class NoiseLevel(Enum):
        QUIET = "quiet"
        NORMAL = "normal"
        NOISY = "noisy"

    noise: Optional[NoiseLevel] = field(default=None)
