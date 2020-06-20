from dataclasses import dataclass

from common import secure
from home.room import Room
from implementations.xiaomi import Gateway
from implementations.yeelight import YeelightColorLamp, YeelightWhiteLamp
from interfaces.connection import HostPort
from interfaces.home import Home

TLV_HOME_ID = 'TLV'
TLV_REMOTE_HOST = secure("ZD8nBBZR")


@dataclass
class TLV(Home):
    appliances = (
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
            key=secure("jqXSLd39")
        ),
    )
