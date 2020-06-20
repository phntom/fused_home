#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import socket
from itertools import chain

import broadlink
from xiaomi_gateway import XiaomiGateway

from common import *

logger = logging.getLogger(__name__)

TAG_NAME = 'sensors'
CONFIG = get_config(TAG_NAME)
DISCONNECTED_FIELD = 'power'
DATA_MAPPING = {
    'RM2': ('temperature',),
    'MP1': ('power',),
    'SP2': ('power', 'nightlight'),
}
DEVICE_COLUMNS = ['power', 'nightlight', 'temperature', 'humidity', 'light', 'air_quality', 'noise', 'voltage',
                  'proto_version', 'status', 'model', 'rgb', 'short_id', 'proto']
INJECT_DEVICES = (
    broadlink.sp2(('192.168.86.78', 80), bytearray(b'@\xb3\xbd4\xea4'), 30023),
    broadlink.sp2(('192.168.86.67', 80), bytearray(b'\x93\xc5Lw\x0fx'), 10035),
    broadlink.sp2(('192.168.86.68', 80), bytearray(b'\x1a\xc6\x19w\x0fx'), 10035),
    broadlink.a1(('192.168.86.77', 80), bytearray(b'q\xd9\x994\xea4'), 10004),
    broadlink.rm(('192.168.86.81', 80), bytearray(b'\xa5\x82X4\xea4'), 10039),
) + tuple(CONFIG['SENSORS_XIAOMI_GATEWAYS'])

FRIENDLY_XIOMI_NAMES = CONFIG['SENSORS_XIAOMI_FRIENDLY_NAMES']


def get_devices():
    devices = broadlink.discover(timeout=CONFIG['SENSORS_BROADLINK_TIMEOUT'])
    devices = [device for device in devices if device.type != 'unknown']
    devices_hosts = {device.host for device in devices}
    for device in INJECT_DEVICES:
        if isinstance(device, dict):
            device = XiaomiGateway(**device)
            for sensor in chain(device.devices.get('sensor', []), device.devices.get('binary_sensor', [])):
                host = ('{}-{}'.format(sensor['sid'], sensor['proto']), int(sensor['short_id']))
                data = sensor['data']
                for k in ('model', 'short_id', 'proto'):
                    data[k] = sensor[k]
                if 'illumination' in data:
                    data['light'] = data.pop('illumination')
                data['friendly_name'] = FRIENDLY_XIOMI_NAMES.get(sensor['sid'], sensor['sid'])
                devices.append((host, data))
        elif device.host not in devices_hosts:
            devices.append(device)
    return devices


def get_host_data_broadlink(device):
    try:
        device.auth()
    except socket.timeout:
        return None, None
    if device.type == 'A1':
        data = device.check_sensors()
    elif device.type not in DATA_MAPPING:
        logger.info('unknown device {} detected on {}:{}', device.type, device.host[0], device.host[1])
        return None, None
    else:
        data = {
            field: getattr(device, f'check_{field}')() for field in DATA_MAPPING[device.type]
        }
    return device.host, data


def get_host_data(device):
    if isinstance(device, tuple):
        return device
    else:
        return get_host_data_broadlink(device)


if __name__ == "__main__":
    main(get_devices, get_host_data, logger, TAG_NAME, DEVICE_COLUMNS, DISCONNECTED_FIELD)
