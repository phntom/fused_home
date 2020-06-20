from dataclasses import dataclass, field, asdict
from itertools import chain
from typing import Optional, Sequence

from xiaomi_gateway import XiaomiGateway

from interfaces.appliance import OnBattery
from interfaces.connection import HostPort
from interfaces.home import ORIGIN_HOME
from interfaces.lamp import ColorLamp
from interfaces.sensor import Motion, Thermometer, Lux, Magnet, Switch

DISCOVERY_RETRIES = 3
INTERFACE = 'any'


@dataclass
class GatewayChild(OnBattery):
    sid: Optional[str] = field(default=None)  # device mac
    model: Optional[str] = field(default=None)
    protocol_version: Optional[str] = field(default=None)


@dataclass
class MotionSensor(Motion, GatewayChild):
    pass


@dataclass
class ThermometerSensor(Thermometer, GatewayChild):
    pass


@dataclass
class MagnetSensor(Magnet, GatewayChild):
    pass


@dataclass
class SwitchSensor(Switch, GatewayChild):
    pass


@dataclass
class Gateway(ColorLamp, Lux):
    host_port: HostPort = field(default=HostPort)
    key: Optional[str] = field(default=None)  # password
    model: Optional[str] = field(default=None)
    protocol_version: Optional[str] = field(default=None)

    def _on_change(self, old_state: dict, new_state: dict):
        pass

    def poll(self) -> Sequence[GatewayChild]:
        host, port = self.host_port.get_pair_for_home(self.home, ORIGIN_HOME)
        gateway = XiaomiGateway(host, port, self.internal_id, self.key, DISCOVERY_RETRIES, INTERFACE)
        for device in gateway.devices:
            for sensor in chain(
                device.devices.get('sensor', []),
                device.devices.get('binary_sensor', [])
            ):
                model = sensor['model']
                protocol_version = sensor['proto']
                data = sensor['data']
                if self.model == 'gateway':
                    self.model = model
                    self.protocol_version = protocol_version
                    self.internal_id = sensor['sid']
                    self.level = Lux.LuxLevel.from_percentage(data['illumination'])  # 1292
                    self.rgb = data['rgb']  # 738137600
                    yield self
                    continue

                res_device = GatewayChild(
                    internal_id=sensor['sid'],
                    friendly_name='TODO:',  # TODO: friendly_name
                    home=self.home,
                    room=self.room,
                    voltage=data['voltage'],
                    read_only=True,
                )
                if model == 'switch':
                    res_device = SwitchSensor(**asdict(res_device))
                elif model == 'motion':
                    res_device = MotionSensor(**asdict(res_device))
                elif model == 'magnet':
                    res_device = MagnetSensor(
                        status=MagnetSensor.Status(data['status']),
                        **asdict(res_device)
                    )
                elif model == 'sensor_ht':
                    res_device = ThermometerSensor(
                        temperature=data['temperature'],
                        humidity=data['humidity'],
                        **asdict(res_device)
                    )
                res_device.poll = self.poll
                yield res_device
