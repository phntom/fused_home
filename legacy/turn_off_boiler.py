#!/usr/bin/env python3

import broadlink

boiler = broadlink.sp2(
    ('192.168.86.78', 80),
    bytearray(b'@\xb3\xbd4\xea4'),
    bytearray(b'V.\x17\x99m\t=(\xdd\xb3\xbaiZ.oX'))
boiler.auth()

if not boiler.check_power():
    exit(0)

exit(0 if boiler.set_power(False) else 500)
