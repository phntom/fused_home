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
CACHE = {}


def fetch_light(ip, port, conn):
    global CACHE
    key = (ip, port)
    entry = CACHE.get(key)
    if entry is None:
        cursor = conn.cursor()
        cols = ', '.join(CAP_COLUMNS)
        cursor.execute(f'SELECT {cols} FROM lights WHERE ip = ? AND port = ? ORDER BY rowid DESC LIMIT 1', key)
        entry = cursor.fetchone()
        CACHE[key] = entry
    return entry


def main(conn):
    while True:
        for bulb in yeelight.discover_bulbs(timeout=5, interface=INTERFACE):
            cursor = conn.cursor()
            ip, port, caps = bulb['ip'], bulb['port'], bulb['capabilities']
            last_entry = fetch_light(ip, port, conn)
            if last_entry is not None:
                last_entry = dict(zip(TABLE_COLUMNS, last_entry))
                if last_entry == caps:
                    continue
            CACHE[(ip, port)] = caps
            caps.update({
                'ip': ip,
                'port': port,
                'date': date.today().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime('%H:%M:%S'),
                'timestamp': int(time()),
            })
            keys = ','.join(caps.keys())
            questions = ','.join(['?'] * len(caps))
            cursor.execute(f'INSERT INTO lights({keys}) VALUES ({questions})', tuple(caps.values()))
        conn.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=expanduser('~/logs/lights.log'),
                        filemode='a+',
                        )
    logger.info(f"started lights monitor, using interface {INTERFACE}")
    conn = sqlite3.connect(expanduser('~/logs/lights.db'))
    columns = ",".join(TABLE_COLUMNS)
    conn.cursor().execute(f"""CREATE TABLE IF NOT EXISTS lights ({columns})""")
    conn.cursor().execute(f"""CREATE INDEX IF NOT EXISTS ip_port ON lights(ip, port)""")
    main(conn)
