#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yeelight

from common import *

logger = logging.getLogger(__name__)

TAG_NAME = 'lights'
DEVICE_COLUMNS = ['id', 'model', 'fw_ver', 'support', 'power', 'bright', 'color_mode', 'ct', 'rgb', 'hue', 'sat',
                  'name']
DISCONNECTED_FIELD = 'power'


def get_devices():
    return yeelight.discover_bulbs(timeout=15, interface=INTERFACE)


def get_host_data(device):
    return (device['ip'], device['port']), device['capabilities']


if __name__ == "__main__":
    main(get_devices, get_host_data, logger, TAG_NAME, DEVICE_COLUMNS, DISCONNECTED_FIELD)
