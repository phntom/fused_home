#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import sqlite3
from os import environ
from datetime import date, datetime
from os.path import expanduser, dirname, abspath, join, exists

from time import time

INTERFACE = environ.get('EXTERNAL_INTERFACE', False)
META_COLUMNS = ['date', 'time', 'timestamp', 'ip', 'port', 'friendly_name']
CACHE = {}

HEARTBEAT_SECONDS = 60 * 60
_LAST_HEARTBEAT = datetime.now()


def starts_with_any(target, prefixes):
    for prefix in prefixes:
        if target.startswith(prefix):
            return True
    return False


def get_config(*args):
    try:
        check = [
            join(dirname(abspath(__file__)), '..', 'common-settings.json'),
            expanduser(join('~', 'logs', 'common-settings.json')),
        ]
        check = [x for x in check if exists(x)]
        if not check:
            raise FileNotFoundError('common-settings.json file not found')
        prefixes = [arg.upper() + '_' for arg in args]
        with open(check[0]) as f:
            logging.info('loading config for {} from {}'.format(args, check[0]))
            return {k: v for (k, v) in json.load(f).items() if starts_with_any(k, prefixes)}
    except Exception:
        logging.exception('failed to load config for {}'.format(args))
        raise


def setup_logging(log_filename):
    formatting = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=formatting,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=expanduser(f'~/logs/{log_filename}'),
        filemode='a+',
    )
    logging.getLogger().addHandler(logging.StreamHandler())


def heartbeat():
    global _LAST_HEARTBEAT
    if (datetime.now() - _LAST_HEARTBEAT).total_seconds() > HEARTBEAT_SECONDS:
        _LAST_HEARTBEAT = datetime.now()
        logging.info(".")


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
    try:
        cursor.execute(f'INSERT INTO {tag_name}({keys}) VALUES ({questions})', tuple(data.values()))
    except sqlite3.InterfaceError:
        logging.exception(f"failed to insert data into {tag_name}\n{data}")
        raise


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
    setup_logging(tag_name + '.log')
    logger.info(f"started {tag_name} monitor, using interface {INTERFACE}")

    conn = sqlite3.connect(expanduser(f'~/logs/{tag_name}.db'))
    conn.cursor().execute(f"""CREATE TABLE IF NOT EXISTS {tag_name} ({",".join(META_COLUMNS + device_columns)})""")
    conn.cursor().execute(f"""CREATE INDEX IF NOT EXISTS ip_port ON {tag_name}(ip, port)""")
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({tag_name})")
    columns = set(META_COLUMNS + device_columns) - {x[1] for x in cursor.fetchall()}
    for column in columns:
        logger.warn(f"adding missing column {column} to {tag_name} table")
        cursor.execute(f"ALTER TABLE {tag_name} ADD {column} NULL")

    seen = set(CACHE.keys())
    cursor = conn.cursor()
    while True:
        try:
            heartbeat()
            for device in get_devices_fn():
                try:
                    host_data = get_host_data_fn(device)
                except Exception:
                    logger.exception('failed to get host data on device {}', device)
                    continue
                host, caps = host_data
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
