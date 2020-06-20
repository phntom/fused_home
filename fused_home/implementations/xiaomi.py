from dataclasses import dataclass, field
from itertools import chain
from typing import Optional

from xiaomi_gateway import XiaomiGateway

from interfaces.appliance import OnBattery
from interfaces.connection import HostPort
from interfaces.home import ORIGIN_HOME
from interfaces.lamp import ColorLamp
from interfaces.sensor import Motion, Thermometer, Lux, Magnet, Switch

DISCOVERY_RETRIES = 3
INTERFACE = 'any'


@dataclass
class Gateway(ColorLamp, Lux):
    host_port: HostPort = field(default=HostPort)
    sid: Optional[str] = field(default=None)  # gateway mac
    key: Optional[str] = field(default=None)  # password

    def _on_change(self, old_state: dict, new_state: dict):
        pass

    def poll(self):
        host, port = self.host_port.get_pair_for_home(self.home, ORIGIN_HOME)
        gateway = XiaomiGateway(host, port, self.sid, self.key, DISCOVERY_RETRIES, INTERFACE)
        for device in gateway.devices:
            for sensor in chain(
                device.devices.get('sensor', []),
                device.devices.get('binary_sensor', [])
            ):
                model = sensor['model']
                data = sensor['data']
                if model == 'gateway':
                    self.brightness = data['illumination']
                    # TODO:
                    continue

                res_device = None
                if model == 'switch':
                    pass
                elif model == 'motion':
                    pass
                elif model == 'magnet':
                    pass
                res_device.voltage = data['voltage']
                yield res_device

                # host = ('{}-{}'.format(sensor['sid'], sensor['proto']), int(sensor['short_id']))
                # data = sensor['data']
                # for k in ('model', 'short_id', 'proto'):
                #     data[k] = sensor[k]
                # if 'illumination' in data:
                #     data['light'] = data.pop('illumination')

                # data['friendly_name'] = FRIENDLY_XIOMI_NAMES.get(sensor['sid'], sensor['sid'])
                # TODO: friendly_name


@dataclass
class GatewayChild(OnBattery):
    sid: Optional[str] = field(default=None)  # device mac
    gateway: Gateway = field(default=Gateway)


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
