import netaddr as netaddr
from netaddr import IPNetwork
from routeros_api import RouterOsApiPool

from common import get_config, setup_logging

setup_logging('routes.log')
CONFIG = get_config('router', 'modem')
ROUTER_KEY = CONFIG['ROUTER_CONFIG']
MODEM_PASSWORD = CONFIG['MODEM_PASSWORD']

router_api = RouterOsApiPool(**ROUTER_KEY).get_api()

route = router_api.get_resource('/ip/route')

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

set_routes = set()

for rrr in route.get(distance=str(ROUTE_DISTANCE)):
    set_routes.add(str(rrr['dst-address']))

add_routes = set()

for addr in router_api.get_resource('/ip/firewall/address-list').get():
    if addr['list'] in hot_lists:
        rng = addr['address'] + '/32'  # '.'.join(addr['address'].split('.')[0:2]) + '.0.0/16'
        if rng in set_routes:
            continue
        add_routes.add(rng)

new_routes = {str(x) for x in
              netaddr.cidr_merge([IPNetwork(x) for x in
                                  add_routes.union(set_routes)])}
new_routes -= set_routes

if not new_routes:
    exit(0)

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

set_routes = {str(rrr['dst-address']) for rrr in route.get(distance=str(ROUTE_DISTANCE))}
minimal_set = {str(x) for x in
               netaddr.cidr_merge([IPNetwork(x) for x in set_routes])}
set_routes -= minimal_set
for rng in set_routes:
    old_id = route.get(**{'dst-address': rng})[0]['id']
    print(f"removing route {rng} {old_id}")
    route.remove(id=old_id)
