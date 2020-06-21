import json
from dataclasses import dataclass, field
from typing import Sequence

from common import secure
from home.room import Room
from implementations.xiaomi import Gateway, SwitchSensor, MotionSensor, ThermometerSensor
from interfaces.appliance import Appliance
from interfaces.connection import HostPort
from interfaces.home import Home

HFA_HOME_ID = 'HFA'
HFA_REMOTE_HOST = secure("kYQ2b4Yf")


@dataclass
class HFA(Home):
    appliances: Sequence[Appliance] = field(default=(
        Gateway(
            friendly_name="Gateway",
            home=HFA_HOME_ID,
            room=Room.BEDROOM,
            host_port=HostPort(
                remote_host=HFA_REMOTE_HOST,
                remote_port=secure("LN3TvFY7"),
                local_host=secure("9Dspm6FH"),
                local_port=9898,
            ),
            internal_id=secure("9v2wrqcA"),
            key=secure("jqXSLd39"),
            child_devices=(
                SwitchSensor(
                    internal_id=secure('5rbf0dJm'),
                    friendly_name='Doorbell',
                    home=HFA_HOME_ID,
                    room=Room.OUTSIDE,
                ),
                SwitchSensor(
                    internal_id=secure('o9SRKsIG'),
                    friendly_name='Living room',
                    home=HFA_HOME_ID,
                    room=Room.LIVING_ROOM,
                ),
                MotionSensor(
                    internal_id=secure('72HFJAxG'),
                    friendly_name='Hallway',
                    home=HFA_HOME_ID,
                    room=Room.HALLWAY,
                ),
                SwitchSensor(
                    internal_id=secure('CI0Uq9Cs'),
                    friendly_name='Bedroom',
                    home=HFA_HOME_ID,
                    room=Room.BEDROOM,
                ),
                ThermometerSensor(
                    internal_id=secure('aDZAXzXY'),
                    friendly_name='Living Room',
                    home=HFA_HOME_ID,
                    room=Room.LIVING_ROOM,
                ),
                ThermometerSensor(
                    internal_id=secure('DGPxmdP2'),
                    friendly_name='Bedroom',
                    home=HFA_HOME_ID,
                    room=Room.BEDROOM,
                ),
            ),
        ),
    ))


if __name__ == '__main__':
    hfa = HFA()
    print(json.dumps(hfa.sensors, indent=4, default=str))
