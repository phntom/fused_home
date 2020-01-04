#!/usr/bin/python3

import requests
from os.path import expanduser

last_line = None
with open(expanduser('~/logs/boiler.log')) as f:
    for line in f:
        if ' ' in line:
            last_line = line

last = last_line.split(' ', 2)[0]

requests.get(f"https://my.kix.co.il/rpi_ping.php?last={last}")
