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
LIGHTS_CAP_COLUMNS = ['id', 'model', 'fw_ver', 'support', 'power', 'bright', 'color_mode', 'ct', 'rgb', 'hue', 'sat', 'name']
META_COLUMNS = ['date', 'time', 'timestamp', 'ip', 'port']
CACHE = {}


def fetch_light(ip, port, cursor):
    global CACHE
    key = (ip, port)
    entry = CACHE.get(key)
    if entry is None:
        cols = ', '.join(LIGHTS_CAP_COLUMNS)
        cursor.execute(f'SELECT {cols} FROM lights WHERE ip = ? AND port = ? ORDER BY rowid DESC LIMIT 1', key)
        entry = cursor.fetchone()
        if entry is None:
            return None
        entry = dict(zip(LIGHTS_CAP_COLUMNS, entry))
        CACHE[key] = entry
    return entry


def main():
    seen = set(CACHE.keys())
    while True:
        seen.clear()
        cursor = conn.cursor()
        for bulb in yeelight.discover_bulbs(timeout=15, interface=INTERFACE):
            ip, port, caps = bulb['ip'], bulb['port'], bulb['capabilities']
            if (ip, port) in seen:
                seen.remove((ip, port))
            last_entry = fetch_light(ip, port, cursor)
            if last_entry is not None and last_entry == caps:
                continue
            CACHE[(ip, port)] = caps.copy()
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
        for ip, port in seen:
            last_entry = CACHE.pop((ip, port))
            last_entry.update({
                'ip': ip,
                'port': port,
                'date': date.today().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime('%H:%M:%S'),
                'timestamp': int(time()),
                'power': 'disconnected',
            })
            keys = ','.join(last_entry.keys())
            questions = ','.join(['?'] * len(last_entry))
            cursor.execute(f'INSERT INTO lights({keys}) VALUES ({questions})', tuple(last_entry.values()))
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

    conn.cursor().execute(f"""CREATE TABLE IF NOT EXISTS lights ({",".join(META_COLUMNS + LIGHTS_CAP_COLUMNS)})""")
    conn.cursor().execute(f"""CREATE INDEX IF NOT EXISTS ip_port ON lights(ip, port)""")

    main()
