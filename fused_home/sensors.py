#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

import broadlink

from common import *

logger = logging.getLogger(__name__)

TAG_NAME = 'sensors'
DISCONNECTED_FIELD = 'power'
DATA_MAPPING = {
    'RM2': ('temperature',),
    'MP1': ('power',),
    'SP2': ('power', 'nightlight'),
}
DEVICE_COLUMNS = ['power', 'nightlight', 'temperature', 'humidity', 'light', 'air_quality', 'noise']
INJECT_DEVICES = (
    broadlink.sp2(('192.168.86.78', 80), bytearray(b'@\xb3\xbd4\xea4'), 30023),
    broadlink.sp2(('192.168.86.67', 80), bytearray(b'\x93\xc5Lw\x0fx'), 10035),
    broadlink.sp2(('192.168.86.68', 80), bytearray(b'\x1a\xc6\x19w\x0fx'), 10035),
    broadlink.a1(('192.168.86.77', 80), bytearray(b'q\xd9\x994\xea4'), 10004),
    broadlink.rm(('192.168.86.81', 80), bytearray(b'\xa5\x82X4\xea4'), 10039),
)


def get_devices():
    devices = broadlink.discover(timeout=15)
    devices = [device for device in devices if device.type != 'unknown']
    devices_hosts = {device.host for device in devices}
    for device in INJECT_DEVICES:
        if device.host not in devices_hosts:
            devices.append(device)
    return devices


def get_host_data(device):
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


if __name__ == "__main__":
    main(get_devices, get_host_data, logger, TAG_NAME, DEVICE_COLUMNS, DISCONNECTED_FIELD)
