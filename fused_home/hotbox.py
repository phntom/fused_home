import re
from datetime import datetime
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

HEARTBEAT_SECONDS = 60*60*3
MODEM_USER = 'admin'
LOG_FILE = '~/.router.key'

session_key_matcher = re.compile(r'.*var sessionkey =[^\d]+(\d+).*', re.DOTALL)
error_counters_matcher = re.compile(r".*<tr align='left'>\n[ \t]*<td height='20'>(\d+)</td>\n[ \t]*<td height='20'>(\d+)</td>.*", re.DOTALL)

last_heartbeat = datetime.now()
logging.info("starting monitoring router")

with open(expanduser(LOG_FILE)) as f:
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
    session_key = session_key_matcher.match(res.text).group(1)
    logging.info("session key is {}".format(session_key))
    res = requests.post(f'http://192.168.100.1/postlogin.cgi?sessionKey={session_key}', data={
        'sessionKey': session_key,
        'loginUsername': MODEM_USER,
        'loginPassword': MODEM_PASSWORD,
    })
    if 'var RefreshPage = ' not in res.text:
        raise ValueError('login failed')

while True:
    if (datetime.now() - last_heartbeat).total_seconds() > HEARTBEAT_SECONDS:
        last_heartbeat = datetime.now()
        logging.info("nothing to report")

    res = requests.get('http://192.168.100.1/reseau-pa3-frequencecable.html')
    res.raise_for_status()
    new_session_key = session_key_matcher.match(res.text).group(1)
    if not session_key:
        session_key = new_session_key
        logging.info("session key is {}".format(session_key))

    m = error_counters_matcher.match(res.text)
    correctable = int(m.group(1))
    uncorrectable = int(m.group(2))

    if uncorrectable > 1:
        logging.warning("found {} correctable and {} uncorrectable errors".format(correctable, uncorrectable))
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
