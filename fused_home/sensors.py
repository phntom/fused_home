#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def get_devices():
    return broadlink.discover(timeout=15)


def get_host_data(device):
    device.auth()
    if device.type == 'A1':
        data = device.check_sensors()
    elif device.type not in DATA_MAPPING:
        logger.info('unknown device {} detected on {}:{}', device.type, *device.host)
        return None, None
    else:
        data = {
            field: getattr(device, f'check_{field}')() for field in DATA_MAPPING[device.type]
        }
    return device.host, data


if __name__ == "__main__":
    main(get_devices, get_host_data, logger, TAG_NAME, DEVICE_COLUMNS, DISCONNECTED_FIELD)
