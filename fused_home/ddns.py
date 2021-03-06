#!/usr/bin/python3
import logging
import socket
from json.decoder import JSONDecodeError
from time import sleep

import linodecli
import requests
from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

from common import setup_logging, heartbeat, get_config


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


def get_local_ipv4(router_api, pppoe_interface):
    results = router_api.get_resource('/ip/address').get(interface=pppoe_interface)
    if results:
        return results[0]['address'].split('/')[0]
    res = requests.get("https://a248.e.akamai.net/whatismyip.akamai.com/")
    res.raise_for_status()
    return res.text


def get_local_ipv6(router_api, ipv6_pool_name):
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect(("2606:4700:4700::1111", 80))
    except OSError:
        return None
    if not s.getsockname():
        return None
    suffix = ':'.join(s.getsockname()[0].split(':')[-4:])

    results = router_api.get_resource('/ipv6/pool').get(name=ipv6_pool_name)
    if results:
        prefix = results[0]['prefix'].split('::')[0]
        return prefix + ':' + suffix

    res = requests.get("http://ip6only.me/api/")
    res.raise_for_status()
    return res.text.split(',')[1]


def main():
    setup_logging('ddns2.log')
    config = get_config('router', 'ddns')

    logging.info("starting ddns")

    ddns_config = config['DDNS_CONFIG']
    resource4 = ddns_config['resource4']
    resource6 = ddns_config['resource6']
    domain = ddns_config['domain']
    pppoe_interface = ddns_config['pppoe_interface']
    ipv6_pool_name = ddns_config['ipv6_pool_name']

    logging.info("loaded config, connecting to router")

    router_api = RouterOsApiPool(**(config['ROUTER_CONFIG'])).get_api()

    while True:
        try:
            for local_ip, resource in (
                (get_local_ipv4(router_api, pppoe_interface), resource4),
                (get_local_ipv6(router_api, ipv6_pool_name), resource6)
            ):
                current_ip, record_name = get_current_record_ip(domain, resource)
                if local_ip is not None and current_ip != local_ip:
                    logging.info(f"updating record {record_name} from {current_ip} to {local_ip}")
                    update_record_ip(domain, resource, local_ip)
            heartbeat()
        except RouterOsApiConnectionError:
            logging.warning('resetting router api')
            router_api = RouterOsApiPool(**(get_config('router')['ROUTER_CONFIG'])).get_api()
        except JSONDecodeError:
            logging.exception('linode JSONDecodeError')
        except (requests.exceptions.RequestException, OSError):
            logging.exception('RequestException issues')
        except:
            logging.exception("error")
            raise
        finally:
            sleep(30)


if __name__ == "__main__":
    main()
