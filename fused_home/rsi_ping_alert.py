from os.path import expanduser
from time import time, sleep

from .irssinotifier import IrssiNotifier


with open(expanduser("~/.irssinotifier.key")) as f:
    API_KEY = f.readline().strip()
    PASSWORD = f.readline().strip()

notifier = IrssiNotifier(API_KEY, PASSWORD)
working = True

while True:
    with open(expanduser('~phantom-web/domains/my.kix.co.il/rpi-last.txt'), 'r') as f:
        try:
            timestamp = float(f.read().strip())
            delta = time() - timestamp
            if delta > 60*5:
                if working:
                    notifier.send_message("i've stopped working", "#maia", "boiler")
                    working = False
            else:
                working = True
        except ValueError:
            pass
    sleep(15)
