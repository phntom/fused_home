from dataclasses import dataclass, field
from typing import Sequence, List, Dict

from interfaces.appliance import Appliance
from interfaces.lamp import Lamp, ColorLamp
from interfaces.sensor import Sensor

ORIGIN_HOME = 'TLV'


@dataclass
class Home:
    appliances: Sequence[Appliance] = field()
    active_appliances: Dict[str, Appliance] = field(default=dict)
    lights: List[Lamp] = field(default=list)
    color_lights: List[ColorLamp] = field(default=list)
    sensors: List[Sensor] = field(default=list)

    def __post_init__(self):
        for appliance in self.appliances:
            self.active_appliances[appliance.id] = appliance
            if isinstance(appliance, Lamp):
                self.lights.append(appliance)
            if isinstance(appliance, ColorLamp):
                self.color_lights.append(appliance)
            if isinstance(appliance, Sensor):
                self.sensors.append(appliance)

