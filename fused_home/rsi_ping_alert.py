from os.path import expanduser
from time import time, sleep

from .irssinotifier import IrssiNotifier

DELAY = 60*10

with open(expanduser("~/.irssinotifier.key")) as f:
    API_KEY = f.readline().strip()
    PASSWORD = f.readline().strip()

notifier = IrssiNotifier(API_KEY, PASSWORD)

notifier.send_message("started monitoring", "#maia", "boiler")
working = True

while True:
    with open(expanduser('~phantom-web/domains/my.kix.co.il/rpi-last.txt'), 'r') as f:
        try:
            timestamp = float(f.read().strip())
            delta = time() - timestamp
            if delta > DELAY and working:
                notifier.send_message("i've stopped working since {}".format(timestamp), "#maia", "boiler")
                working = False
            elif delta <= DELAY and not working:
                notifier.send_message("working again since {}".format(timestamp), "#maia", "boiler")
                working = True
        except ValueError:
            pass
    sleep(15)
