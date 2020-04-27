#!/usr/bin/python3
import json
import logging
import socket
from json.decoder import JSONDecodeError

import linodecli
from os.path import expanduser
from time import sleep

import requests
import urllib3
from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

from common import setup_logging, heartbeat


def get_current_record_ip(domain, resource):
    records_view = linodecli.cli.ops['domains']['records-view']
    res = linodecli.cli.do_request(records_view, [domain, resource])
    res.raise_for_status()
    j = res.json()
    return j['target'], j['name']


def update_record_ip(domain, resource, new_ip):
    records_update = linodecli.cli.ops['domains']['records-update']
    res = linodecli.cli.do_request(records_update, [
        domain,
        resource,
        '--target',
        new_ip,
        '--type',
        'AAAA' if ':' in new_ip else 'A'
    ])
    res.raise_for_status()
    logging.info(res.text)


def get_local_ipv4(router_api):
    results = router_api.get_resource('/ip/address').get(interface='pppoe-out1')
    if results:
        return results[0]['address'].split('/')[0]
    res = requests.get("https://a248.e.akamai.net/whatismyip.akamai.com/")
    res.raise_for_status()
    return res.text


def get_local_ipv6(router_api):
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.connect(("2606:4700:4700::1111", 80))
    if not s.getsockname():
        return None
    suffix = ':'.join(s.getsockname()[0].split(':')[-4:])

    results = router_api.get_resource('/ipv6/pool').get(name='hotnet1')
    if results:
        prefix = results[0]['prefix'].split('::')[0]
        return prefix + ':' + suffix

    res = requests.get("http://ip6only.me/api/")
    res.raise_for_status()
    return res.text.split(',')[1]


def main():
    setup_logging('ddns2.log')
    resource4 = "6363291"
    resource6 = "15198378"
    domain = "114584"
    logging.info("starting ddns")
    with open(expanduser('~/.router.key')) as f:
        router_key = json.load(f)
        router_key.pop('MODEM_PASSWORD')
    router_api = RouterOsApiPool(**router_key).get_api()
    while True:
        try:
            for local_ip, resource in (
                (get_local_ipv4(router_api), resource4),
                (get_local_ipv6(router_api), resource6)
            ):
                current_ip, record_name = get_current_record_ip(domain, resource)
                if current_ip != local_ip:
                    logging.info(f"updating record {record_name} from {current_ip} to {local_ip}")
                    update_record_ip(domain, resource, local_ip)
            heartbeat()
        except RouterOsApiConnectionError:
            router_api = RouterOsApiPool(**router_key).get_api()
            logging.warning('resetting router api')
        except JSONDecodeError:
            logging.exception('linode JSONDecodeError')
        except (requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError, urllib3.exceptions.MaxRetryError):
            logging.exception('connection issues')
        except:
            logging.exception("error")
        finally:
            sleep(30)


if __name__ == "__main__":
    main()
