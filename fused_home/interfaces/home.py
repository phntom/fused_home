from dataclasses import dataclass, field
from typing import Sequence, Dict, List

from implementations.events import EventBus
from interfaces.appliance import Appliance
from interfaces.events import EventBus as EventBusInterface
from interfaces.lamp import Lamp, ColorLamp
from interfaces.sensor import Sensor

ORIGIN_HOME = 'TLV'


@dataclass
class Home:
    appliances: Sequence[Appliance] = field(default_factory=tuple)
    active_appliances: Dict[str, Appliance] = field(default_factory=dict)
    lights: List[Lamp] = field(default_factory=list)
    color_lights: List[ColorLamp] = field(default_factory=list)
    sensors: List[Sensor] = field(default_factory=list)
    events: EventBusInterface = field(default_factory=EventBus)

    def __post_init__(self):
        for appliance_pre_expand in self.appliances:
            for appliance in appliance_pre_expand.expand():
                self.active_appliances[appliance.id] = appliance
                if isinstance(appliance, Lamp):
                    self.lights.append(appliance)
                if isinstance(appliance, ColorLamp):
                    self.color_lights.append(appliance)
                if isinstance(appliance, Sensor):
                    self.sensors.append(appliance)
