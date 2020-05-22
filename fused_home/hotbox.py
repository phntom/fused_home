import re
from time import sleep

import json
import logging
import requests
from os.path import expanduser
from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError

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
        logging.warning("Permission denied, another user is already logged; sleeping 20 seconds")
        sleep(20)
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
        logging.info(f"cookie is {session.cookies}")
        return session_key

    if not session.cookies:
        logging.warning(f"need to force logout and log back in for reboot to work")
        session.get('http://192.168.100.1/logout.html').raise_for_status()
        return ''

    new_session_key = session_key_matcher.match(res.text).group(1)
    if new_session_key and new_session_key != session_key:
        session_key = new_session_key

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

        logging.warning("restarting cable modem; session key is {}, cookies {}".format(session_key, session.cookies))

        res = session.post(f'http://192.168.100.1/reseau-pa3-frequencecable.cgi?sessionKey={session_key}', data={
            'sessionKey': session_key,
            'CmStartupDsFreq': '999999',
            'action': '1',
        })
        res.raise_for_status()
        if 'Invalid Session Key' in res.text:
            logging.warning('Invalid Session Key error, logging out and retrying')
            session.get('http://192.168.100.1/logout.html').raise_for_status()
            return ''

        logging.warning("disabling eth interface on router")
        eth = router_api.get_resource('/interface')
        eth_id = eth.get(name='wan-hot')[0]['id']
        eth.set(id=eth_id, disabled='yes')

        logging.warning("waiting 125 seconds")
        sleep(120)

        eth.set(id=eth_id, disabled='no')
        logging.warning("reenabling cable modem interface")
        sleep(5)

        logging.warning("reenabling cable modem route")
        route.set(id=route_id, disabled='yes')

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
        except (OSError, requests.exceptions.ConnectionError, RouterOsApiConnectionError):
            logging.exception('HTTP connection exception; sleeping 10 seconds')
            sleep(10)
        except Exception:
            logging.exception('unhandled exception')
            raise
