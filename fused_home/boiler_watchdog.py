#!/usr/bin/env python3
import logging
from datetime import datetime, timedelta
from time import sleep, time
import broadlink
from os.path import expanduser

import requests
from requests import HTTPError

logger = logging.getLogger(__name__)

BOILER_TARGET = (('192.168.86.78', 80), bytearray(b'@\xb3\xbd4\xea4'), bytearray(b'V.\x17\x99m\t=(\xdd\xb3\xbaiZ.oX'))
BOILER_TIMEOUT_MINUTES = 18


class Watchdog(object):
    def __init__(self):
        self.prev_state = None
        self.prev_time = None
        self.boiler = broadlink.sp2(*BOILER_TARGET)

    def main(self):
        on = self.boiler.check_power()

        if on is None:
            raise RuntimeError("invalid response from boiler")

        if on != self.prev_state:
            logger.info("boiler is now {}".format("on" if on else "off"))
            self.prev_time = datetime.now()
            self.prev_state = on
            with open(expanduser('~/logs/boiler.log'), 'a+') as w:
                w.write("{} {}\n".format(time(), int(on)))

        duration = datetime.now() - self.prev_time
        if on and duration > timedelta(minutes=BOILER_TIMEOUT_MINUTES):
            logger.warning("boiler is on for {} - turning it off".format(duration))
            while self.boiler.check_power():
                self.boiler.set_power(False)
                sleep(5)
            self.prev_time = datetime.now()
            self.prev_state = on


def rsi_ping():
    requests.get('https://my.kix.co.il/rpi_ping.php', params=[('last', str(time()))], ).raise_for_status()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=expanduser('~/logs/boiler_watchdog.log'),
                        filemode='a+')
    logger.info("started, monitoring boiler {}, {}, {}".format(*BOILER_TARGET))

    while True:
        try:
            wd = Watchdog()

            while not wd.boiler.auth():
                logger.error("failed to authenticate to boiler")
                sleep(10)
            logger.info("authenticated to boiler")

            while True:
                wd.main()
                rsi_ping()
                sleep(15)
        except HTTPError:
            logger.warning("internet is down, cannot reach my.kix.co.il")
            sleep(30)
        except KeyboardInterrupt:
            logger.info("bye bye")
            exit(0)
        except Exception as e:
            logger.exception("unexpected error, restarting", e)
            sleep(10)
