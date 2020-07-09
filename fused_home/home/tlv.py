import json
from dataclasses import dataclass, field
from typing import Sequence

from xiaomi_gateway import XiaomiGatewayDiscovery

from common import secure
from home.room import Room
from implementations.xiaomi import Gateway, ThermometerSensor, MagnetSensor, MotionSensor, SwitchSensor
from implementations.yeelight import YeelightColorLamp, YeelightWhiteLamp
from interfaces.appliance import Appliance
from interfaces.connection import HostPort
from interfaces.home import Home

TLV_HOME_ID = 'TLV'
TLV_REMOTE_HOST = secure("ZD8nBBZR")


@dataclass
class TLV(Home):
    appliances: Sequence[Appliance] = field(default=(
        YeelightWhiteLamp(
            friendly_name="Entrance",
            internal_id="entrance",
            home=TLV_HOME_ID,
            room=Room.ENTRANCE,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("nzxTLerH"),
                local_host=secure("tfBa8xF7"),
                local_port=55443,
            ),
        ),
        YeelightWhiteLamp(
            friendly_name="Kitchen",
            internal_id="kitchen",
            home=TLV_HOME_ID,
            room=Room.KITCHEN,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("qCCWxn93"),
                local_host=secure("NazFt55x"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Desk",
            internal_id="desk",
            home=TLV_HOME_ID,
            room=Room.LIVING_ROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("2fSqpfVu"),
                local_host=secure("wE6VVYVc"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Living room C1",
            internal_id="living_room_c1",
            home=TLV_HOME_ID,
            room=Room.LIVING_ROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("vKUmkBWG"),
                local_host=secure("a6WUgt3t"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Living room C2",
            internal_id="living_room_c2",
            home=TLV_HOME_ID,
            room=Room.LIVING_ROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("fAMDYtYD"),
                local_host=secure("8nszb3Dq"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Living room C3",
            internal_id="living_room_c3",
            home=TLV_HOME_ID,
            room=Room.LIVING_ROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("L2A7wVLn"),
                local_host=secure("CpzcnGwW"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Living room C4",
            internal_id="living_room_c4",
            home=TLV_HOME_ID,
            room=Room.LIVING_ROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("7BSN9nrT"),
                local_host=secure("BEavgGvf"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Living room C5",
            internal_id="living_room_c5",
            home=TLV_HOME_ID,
            room=Room.LIVING_ROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("pGzumGZS"),
                local_host=secure("nPUF7M5Z"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Bedroom",
            internal_id="bedroom",
            home=TLV_HOME_ID,
            room=Room.BEDROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("EDbwDSbw"),
                local_host=secure("Y897z9tS"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Bedroom Strip",
            internal_id="strip",
            home=TLV_HOME_ID,
            room=Room.BEDROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("6JCdgH4t"),
                local_host=secure("dXVwASXT"),
                local_port=55443,
            ),
        ),
        YeelightColorLamp(
            friendly_name="Bathroom",
            internal_id="bathroom",
            home=TLV_HOME_ID,
            room=Room.BATHROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("W3k3qRAM"),
                local_host=secure("gjh9dNeN"),
                local_port=55443,
            ),
        ),
        Gateway(
            friendly_name="Gateway",
            home=TLV_HOME_ID,
            room=Room.BEDROOM,
            host_port=HostPort(
                remote_host=TLV_REMOTE_HOST,
                remote_port=secure("g7P8bZTN"),
                local_host=secure("wWW5NNZv"),
                local_port=9898,
            ),
            internal_id=secure("9v2wrqcA"),
            key=secure("jqXSLd39"),
            child_devices=(
                ThermometerSensor(
                    internal_id=secure('htXYpdRz'),
                    friendly_name='Living Room',
                    home=TLV_HOME_ID,
                    room=Room.LIVING_ROOM,
                ),
                ThermometerSensor(
                    internal_id=secure('cHTAJFV9'),
                    friendly_name='Outside',
                    home=TLV_HOME_ID,
                    room=Room.OUTSIDE,
                ),
                ThermometerSensor(
                    internal_id=secure('1RhB9iq5'),
                    friendly_name='Bedroom',
                    home=TLV_HOME_ID,
                    room=Room.BEDROOM,
                ),
                SwitchSensor(
                    internal_id=secure('lEB2WUMo'),
                    friendly_name='Bedroom Light',
                    home=TLV_HOME_ID,
                    room=Room.BEDROOM,
                ),
                SwitchSensor(
                    internal_id=secure('w6iHYjBq'),
                    friendly_name='Entrance',
                    home=TLV_HOME_ID,
                    room=Room.ENTRANCE,
                ),
                SwitchSensor(
                    internal_id=secure('USjla5rK'),
                    friendly_name='Living Room',
                    home=TLV_HOME_ID,
                    room=Room.LIVING_ROOM,
                ),
                MotionSensor(
                    internal_id=secure('YPlzVafY'),
                    friendly_name='Kitchen',
                    home=TLV_HOME_ID,
                    room=Room.KITCHEN,
                ),
                MotionSensor(
                    internal_id=secure('1phUj4N9'),
                    friendly_name='Bathroom',
                    home=TLV_HOME_ID,
                    room=Room.BATHROOM,
                ),
                MotionSensor(
                    internal_id=secure('IDkcKyz0'),
                    friendly_name='Entrance',
                    home=TLV_HOME_ID,
                    room=Room.ENTRANCE,
                ),
                MotionSensor(
                    internal_id=secure('qRKPircm'),
                    friendly_name='Living Room',
                    home=TLV_HOME_ID,
                    room=Room.LIVING_ROOM,
                ),
                SwitchSensor(
                    internal_id=secure('MSI8dMQG'),
                    friendly_name='Bedroom AC',
                    home=TLV_HOME_ID,
                    room=Room.BEDROOM,
                ),
                MotionSensor(
                    internal_id=secure('cvoXNqgf'),
                    friendly_name='Bathroom Aft',
                    home=TLV_HOME_ID,
                    room=Room.BATHROOM,
                ),
                MagnetSensor(
                    internal_id=secure('tMDVswsX'),
                    friendly_name='Living Room Window',
                    home=TLV_HOME_ID,
                    room=Room.LIVING_ROOM,
                ),
                MagnetSensor(
                    internal_id=secure('ZK5PE0Eh'),
                    friendly_name='Bedroom Window Right',
                    home=TLV_HOME_ID,
                    room=Room.BEDROOM,
                ),
                MagnetSensor(
                    internal_id=secure('eq3mWGYk'),
                    friendly_name='Bedroom Window Left',
                    home=TLV_HOME_ID,
                    room=Room.BEDROOM,
                ),
            ),
        ),
    ))


if __name__ == '__main__':
    tlv = TLV()
    print(json.dumps(tlv.sensors, indent=4, default=str))
