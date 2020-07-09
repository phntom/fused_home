import json
from dataclasses import dataclass, field, asdict
from itertools import chain
from typing import Optional, Sequence, Dict

from xiaomi_gateway import XiaomiGateway

from interfaces.appliance import OnBattery, Appliance
from interfaces.connection import HostPort
from interfaces.home import ORIGIN_HOME
from interfaces.lamp import ColorLamp
from interfaces.sensor import Motion, Thermometer, Lux, Magnet, Switch

DISCOVERY_RETRIES = 3
INTERFACE = 'any'


class _GatewayMixin(Appliance):
    pass


@dataclass
class GatewayChild(_GatewayMixin, OnBattery):
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


class ExtendedXiaomiGateway(XiaomiGateway):
    @property
    def protocol(self):
        return int(self.proto[0:1])

    def report(self, sid, model, key1, key2, value):
        payload = {'cmd': 'write', 'model': model, 'sid': sid}
        if self.protocol == 1:
            payload['data'] = {key1: value, 'key': self._get_key()}
        else:
            payload['params'] = [{key2: value, 'key': self._get_key()}]
        cmd = json.dumps(payload, separators=(',', ':'))
        print(cmd)
        resp = self._send_cmd(cmd, 'write_ack')
        print(resp)
        return self.push_data(resp)


@dataclass
class Gateway(_GatewayMixin, ColorLamp, Lux):
    host_port: HostPort = field(default=HostPort)
    key: Optional[str] = field(default=None)  # password
    model: Optional[str] = field(default=None)
    protocol_version: Optional[str] = field(default=None)
    child_devices: Sequence[GatewayChild] = field(default_factory=tuple)
    _children: Dict[str, GatewayChild] = field(default_factory=dict)

    def _on_change(self, old_state: dict, new_state: dict):
        pass

    def expand(self):
        host, port = self.host_port.get_pair_for_home(self.home, ORIGIN_HOME)
        gateway = ExtendedXiaomiGateway(host, port, self.internal_id, self.key, DISCOVERY_RETRIES, INTERFACE)
        self._gateway = gateway

        for child_device in self.child_devices:
            if child_device.internal_id not in self._children:
                self._children[child_device.internal_id] = child_device

        for sensors in chain(gateway.devices.values()):
            for sensor in sensors:
                mac = sensor['sid']
                model = sensor['model']
                protocol_version = sensor['proto']
                data = sensor['data']
                if self.model == 'gateway':
                    self.model = model
                    self.protocol_version = protocol_version
                    self.internal_id = mac
                    self.level = Lux.LuxLevel.from_percentage(data['illumination'])  # 1292
                    self.rgb = data['rgb']  # 738137600
                    yield self
                    continue

                res_device = GatewayChild(
                    internal_id=mac,
                    friendly_name=f'Unknown {mac}',
                    home=self.home,
                    room=self.room,
                ) if mac not in self._children else self._children[mac]
                res_device.voltage = data.get('voltage', None)
                res_device.read_only = True

                if model == 'switch' and not isinstance(res_device, SwitchSensor):
                    res_device = SwitchSensor(**asdict(res_device))
                elif model == 'motion' and not isinstance(res_device, MotionSensor):
                    res_device = MotionSensor(**asdict(res_device))
                elif model == 'magnet':
                    if not isinstance(res_device, MagnetSensor):
                        res_device = MagnetSensor(**asdict(res_device))
                    res_device.status = MagnetSensor.Status(data['status'])
                elif model == 'sensor_ht':
                    if not isinstance(res_device, ThermometerSensor):
                        res_device = ThermometerSensor(**asdict(res_device))
                    res_device.temperature = data['temperature']
                    res_device.humidity = data['humidity']

                self._children[mac] = res_device
                yield res_device
