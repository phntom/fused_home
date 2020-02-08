#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sqlite3
from os import environ
from datetime import date, datetime
from os.path import expanduser

from time import time

INTERFACE = environ.get('EXTERNAL_INTERFACE', False)
META_COLUMNS = ['date', 'time', 'timestamp', 'ip', 'port']
CACHE = {}


def fetch_entry(host, cursor, tag_name, device_columns):
    entry = CACHE.get(host)
    if entry is None:
        cols = ', '.join(device_columns)
        cursor.execute(f'SELECT {cols} FROM {tag_name} WHERE ip = ? AND port = ? ORDER BY rowid DESC LIMIT 1', host)
        entry = cursor.fetchone()
        if entry is None:
            return None
        entry = dict(zip(device_columns, entry))
        CACHE[host] = entry
    return entry


def process_device(host, data, seen, cache, cursor, tag_name, device_columns):
    if host in seen:
        seen.remove(host)
    last_entry = fetch_entry(host, cursor, tag_name, device_columns)
    if last_entry is not None and last_entry == data:
        return
    cache[host] = data.copy()
    data.update({
        'ip': host[0],
        'port': host[1],
        'date': date.today().strftime("%Y-%m-%d"),
        'time': datetime.now().strftime('%H:%M:%S'),
        'timestamp': int(time()),
    })
    keys = ','.join(data.keys())
    questions = ','.join(['?'] * len(data))
    cursor.execute(f'INSERT INTO {tag_name}({keys}) VALUES ({questions})', tuple(data.values()))


def process_unseen(cursor, seen, tag_name, disconnected_field):
    for ip, port in seen:
        last_entry = CACHE.pop((ip, port))
        last_entry.update({
            'ip': ip,
            'port': port,
            'date': date.today().strftime("%Y-%m-%d"),
            'time': datetime.now().strftime('%H:%M:%S'),
            'timestamp': int(time()),
            disconnected_field: 'disconnected',
        })
        keys = ','.join(last_entry.keys())
        questions = ','.join(['?'] * len(last_entry))
        cursor.execute(f'INSERT INTO {tag_name}({keys}) VALUES ({questions})', tuple(last_entry.values()))


def main(get_devices_fn, get_host_data_fn, logger, tag_name, device_columns, disconnected_field):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=expanduser(f'~/logs/{tag_name}.log'),
                        filemode='a+',
                        )
    logger.info(f"started {tag_name} monitor, using interface {INTERFACE}")

    conn = sqlite3.connect(expanduser(f'~/logs/{tag_name}.db'))
    conn.cursor().execute(f"""CREATE TABLE IF NOT EXISTS {tag_name} ({",".join(META_COLUMNS + device_columns)})""")
    conn.cursor().execute(f"""CREATE INDEX IF NOT EXISTS ip_port ON {tag_name}(ip, port)""")

    seen = set(CACHE.keys())
    cursor = conn.cursor()
    while True:
        try:
            for device in get_devices_fn():
                host, caps = get_host_data_fn(device)
                if host is None:
                    continue
                try:
                    process_device(host, caps, seen, CACHE, cursor, tag_name, device_columns)
                except Exception:
                    logger.exception('failed to process {}:{}', *host)
            process_unseen(cursor, seen, tag_name, disconnected_field)
            seen.clear()
            conn.commit()
        except Exception:
            logger.exception('loop failed')
