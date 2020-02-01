#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sqlite3
from os.path import expanduser

import yeelight

logger = logging.getLogger(__name__)

TABLE_COLUMNS = ['ip', 'port', 'id', 'model', 'fw_ver', 'support', 'power', 'bright', 'color_mode', 'ct', 'rgb',
                 'hue', 'sat', 'name']


def main(c):
    global TABLE_COLUMNS
    while True:
        for bulb in yeelight.discover_bulbs(timeout=5):
            ip, port, caps = bulb['ip'], bulb['port'], bulb['capabilities']
            caps['ip'] = ip
            caps['port'] = port
            c.execute('SELECT * FROM lights WHERE ip = ? AND port = ? ORDER BY rowid DESC LIMIT 1', (ip, port))
            last_entry = c.fetchone()
            if last_entry is not None:
                last_entry = dict(zip(TABLE_COLUMNS, last_entry))
                if last_entry == caps:
                    continue
            keys = ','.join(caps.keys())
            questions = ','.join(['?'] * len(caps))
            c.execute(f'INSERT INTO lights({keys}) VALUES ({questions})', tuple(caps.values()))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=expanduser('~/logs/lights.log'),
                        filemode='a+')
    logger.info("started lights monitor")
    c = sqlite3.connect(expanduser('~/logs/lights.db')).cursor()
    columns = ",".join(TABLE_COLUMNS)
    c.execute(f"""CREATE TABLE IF NOT EXISTS lights ({columns})""")
    main(c)
