import re
from datetime import datetime
from time import sleep

import json
import logging
import requests
from os.path import expanduser
from routeros_api import RouterOsApiPool

from common import setup_logging, heartbeat

HEARTBEAT_SECONDS = 60 * 60 * 1
MODEM_USER = 'admin'
ROUTER_KEY_FILE = '~/.router.key'

session_key_matcher = re.compile(r'.*var sessionkey =[^\d]+(\d+).*', re.DOTALL)
error_counters_matcher = re.compile(
    r".*<tr align='left'>\n[ \t]*<td height='20'>(\d+)</td>\n[ \t]*<td height='20'>(\d+)</td>.*", re.DOTALL)

with open(expanduser(ROUTER_KEY_FILE)) as f:
    ROUTER_KEY = json.load(f)
MODEM_PASSWORD = ROUTER_KEY.pop('MODEM_PASSWORD')


def main_loop(session_key, session):
    res = session.get('http://192.168.100.1/reseau-pa3-frequencecable.html')
    res.raise_for_status()

    if 'document.write(AccessMemberLimit);' in res.text:
        logging.warning("Permission denied, another user is already logged; Sleeping 120 seconds")
        sleep(120)
        return session_key

    if '>location.href="/login.html"<' in res.text:
        logging.info("logging in to session")
        # login
        res = session.get('http://192.168.100.1/login.html')
        res.raise_for_status()
        session_key = session_key_matcher.match(res.text).group(1)
        logging.info("session key is {}".format(session_key))
        res = session.post(f'http://192.168.100.1/postlogin.cgi?sessionKey={session_key}', data={
            'sessionKey': session_key,
            'loginUsername': MODEM_USER,
            'loginPassword': MODEM_PASSWORD,
        })
        if 'var RefreshPage = ' not in res.text:
            raise ValueError('login failed')
        return session_key

    new_session_key = session_key_matcher.match(res.text).group(1)
    if new_session_key and not session_key:
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

        res = session.post(f'http://192.168.100.1/rebootinfo.cgi?sessionKey={session_key}', data={
            'sessionKey': session_key,
        })
        res.raise_for_status()

        logging.warning("waiting 15 seconds")
        sleep(15)

        logging.warning("reenabling cable modem route")
        route.set(id=route_id, disabled='no')

        logging.warning("waiting 105 seconds")
        sleep(100)

    return session_key


if __name__ == '__main__':
    setup_logging('router.log')
    s_key = None
    logging.info("starting monitoring router")
    requests_session = requests.Session()

    while True:
        try:
            heartbeat()
            s_key = main_loop(s_key, requests_session)
            sleep(5)
        except Exception:
            logging.exception('unhandled exception')
            raise
