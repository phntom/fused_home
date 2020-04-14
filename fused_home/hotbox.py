import re
from time import sleep

import json
import logging
import requests
from os.path import expanduser
from routeros_api import RouterOsApiPool

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=expanduser(f'~/logs/router.log'),
                    filemode='a+',
                    )

with open(expanduser("~/.router.key")) as f:
    ROUTER_KEY = json.load(f)
MODEM_PASSWORD = ROUTER_KEY.pop('MODEM_PASSWORD')

res = requests.get('http://192.168.100.1/reseau-pa3-frequencecable.html')
res.raise_for_status()
session_key = None
if '>location.href="/login.html"<' in res.text:
    logging.info("logging in to session")
    # login
    res = requests.get('http://192.168.100.1/login.html')
    res.raise_for_status()
    session_key = re.compile(r'.*var sessionkey = ..(\d+).*', re.DOTALL).match(res.text).group(1)
    logging.info("session key is {}".format(session_key))
    res = requests.post(f'http://192.168.100.1/postlogin.cgi?sessionKey={session_key}', data={
        'sessionKey': session_key,
        'loginUsername': 'admin',
        'loginPassword': MODEM_PASSWORD,
    })
    if 'var RefreshPage = ' not in res.text:
        raise ValueError('login failed')

while True:
    res = requests.get('http://192.168.100.1/reseau-pa3-frequencecable.html')
    res.raise_for_status()
    error_counters_matcher = re.compile(r".*<tr align='left'>\n[ \t]*<td height='20'>(\d+)</td>\n[ \t]*<td height='20'>(\d+)</td>.*", re.DOTALL)
    m = error_counters_matcher.match(res.text)
    correctable = int(m.group(1))
    uncorrectable = int(m.group(2))
    logging.warning("found {} correctable and {} uncorrectable errors".format(correctable, uncorrectable))

    if uncorrectable > 1:
        logging.warning("disabling cable modem route")
        router_api = RouterOsApiPool(**ROUTER_KEY).get_api()
        route = router_api.get_resource('/ip/route')
        route_id = route.get(distance='15')[0]['id']
        route.set(id=route_id, disabled='no')

        logging.warning("restarting cable modem")

        res = requests.post(f'http://192.168.100.1/reseau-pa3-frequencecable.cgi?sessionKey={session_key}', data={
            'sessionKey': session_key,
            'CmStartupDsFreq': '999999',
            'action': '1',
        })
        res.raise_for_status()

        logging.warning("waiting 15 seconds")
        sleep(15)

        logging.warning("reenabling cable modem route")
        route.set(id=route_id, disabled='no')

        logging.warning("waiting 105 seconds")
        sleep(100)

    sleep(5)
