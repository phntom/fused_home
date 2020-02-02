#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sqlite3
from datetime import date, datetime
from os import environ
from time import time
from os.path import expanduser

import yeelight

logger = logging.getLogger(__name__)

INTERFACE = environ.get('EXTERNAL_INTERFACE', False)
CAP_COLUMNS = ['id', 'model', 'fw_ver', 'support', 'power', 'bright', 'color_mode', 'ct', 'rgb', 'hue', 'sat', 'name']
TABLE_COLUMNS = ['date', 'time', 'timestamp', 'ip', 'port'] + CAP_COLUMNS


def main(c):
    global TABLE_COLUMNS, CAP_COLUMNS, INTERFACE
    while True:
        for bulb in yeelight.discover_bulbs(timeout=5, interface=INTERFACE):
            ip, port, caps = bulb['ip'], bulb['port'], bulb['capabilities']
            cols = ', '.join(CAP_COLUMNS)
            c.execute(f'SELECT {cols} FROM lights WHERE ip = ? AND port = ? ORDER BY rowid DESC LIMIT 1', (ip, port))
            last_entry = c.fetchone()
            if last_entry is not None:
                last_entry = dict(zip(TABLE_COLUMNS, last_entry))
                if last_entry == caps:
                    continue
            caps.update({
                'ip': ip,
                'port': port,
                'date': date.today().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime('%H:%M:%S'),
                'timestamp': int(time()),
            })
            keys = ','.join(caps.keys())
            questions = ','.join(['?'] * len(caps))
            c.execute(f'INSERT INTO lights({keys}) VALUES ({questions})', tuple(caps.values()))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=expanduser('~/logs/lights.log'),
                        filemode='a+',
                        )
    logger.info(f"started lights monitor, using interface {INTERFACE}")
    c = sqlite3.connect(expanduser('~/logs/lights.db')).cursor()
    columns = ",".join(TABLE_COLUMNS)
    c.execute(f"""CREATE TABLE IF NOT EXISTS lights ({columns})""")
    main(c)
