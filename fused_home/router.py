from time import sleep

import netaddr as netaddr
from netaddr import IPNetwork
from routeros_api import RouterOsApiPool

from common import get_config, setup_logging, heartbeat

ROUTE_DISTANCE = 39

hot_lists = {
    'google',
    'com.instagram',
    'com.netflix',
    'youtube',
    'facebook',
    'net.fbcdn',
    'com.fast',
    'netflix',
    'net.akamaihd',
    'com.facebook',
    'net.nflxvideo',
    'akamai',
    'com.amazon',
    'com.amazonaws',
    'com.spotify',
    'com.steampowered',
    'com.linode.speedtest',
}


def load_existing_routes(route, set_routes):
    for rrr in route.get(distance=str(ROUTE_DISTANCE)):
        set_routes.add(str(rrr['dst-address']))


def load_address_list(router_api, set_routes, add_routes):
    for addr in router_api.get_resource('/ip/firewall/address-list').get():
        if addr['list'] in hot_lists:
            rng = addr['address'] + '/32'  # '.'.join(addr['address'].split('.')[0:2]) + '.0.0/16'
            if rng in set_routes:
                continue
            add_routes.add(rng)
    add_routes = add_routes.union(set_routes)
    new_routes = {str(x) for x in netaddr.cidr_merge([IPNetwork(x) for x in add_routes])}
    remove_routes = set_routes - new_routes
    new_routes -= set_routes
    return new_routes, remove_routes


def add_new_routes(route, new_routes, remove_routes):
    for rng in new_routes:
        print(f"adding route {rng}")
        route.add(gateway='100.96.40.1',
                  distance=str(ROUTE_DISTANCE),
                  scope='30',
                  **{
                      'target-scope': '10',
                      'dst-address': str(rng),
                      'check-gateway': 'ping',
                  })
    for rng in remove_routes:
        old_id = route.get(**{'dst-address': rng})[0]['id']
        print(f"removing route {rng} {old_id}")
        route.remove(id=old_id)


def add_fast_routes(add_routes, connections):
    for connection in connections.get():
        if connection['protocol'] != 'tcp' or connection['tcp-state'] != 'established':
            continue
        orig_rate = int(connection['orig-rate'])
        repl_rate = int(connection['repl-rate'])
        rng = connection['dst-address'].split(':')[0] + '/32'
        if rng in add_routes:
            continue
        if repl_rate > 8192000:
            print('download speed {}mb for connection {} --> {}'.format(
                connection['dst-address'], connection['src-address'], repl_rate/8/1024/1024)
            )
            add_routes.add(rng)
        if orig_rate > 8192000:
            print('upload speed {}mb for connection {} --> {}'.format(
                connection['dst-address'], connection['src-address'], repl_rate/8/1024/1024)
            )
            add_routes.add(rng)


def main():
    set_routes = set()
    add_routes = set()
    setup_logging('routes.log')
    config = get_config('router')
    router_key = config['ROUTER_CONFIG']
    router_api = RouterOsApiPool(**router_key).get_api()
    route = router_api.get_resource('/ip/route')
    load_existing_routes(route, set_routes)
    connections = router_api.get_resource('/ip/firewall/connection')
    while True:
        heartbeat()
        add_routes.clear()
        add_fast_routes(add_routes, connections)
        new_routes, remove_routes = load_address_list(router_api, set_routes, add_routes)
        if new_routes:
            add_new_routes(route, new_routes, remove_routes)
            set_routes -= remove_routes
            set_routes = set_routes.union(new_routes)
        sleep(30)


if __name__ == '__main__':
    main()
