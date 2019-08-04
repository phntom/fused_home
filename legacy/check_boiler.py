#!/usr/bin/env python3
import time
import broadlink
from os.path import expanduser

boiler = broadlink.sp2(
    ('192.168.86.78', 80),
    bytearray(b'@\xb3\xbd4\xea4'),
    bytearray(b'V.\x17\x99m\t=(\xdd\xb3\xbaiZ.oX'))
boiler.auth()

state = boiler.check_power()

with open(expanduser('~/fused_home/legacy/boiler.log'), 'a+') as w:
    w.write("{} {}\n".format(time.time(), int(state)))

exit(200 if state else 204)
