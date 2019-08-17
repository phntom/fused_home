from os.path import expanduser
from time import time, sleep

from fused_home.irssinotifier import IrssiNotifier


with open(expanduser("~/.irssinotifier.key")) as f:
    API_KEY = f.readline().strip()
    PASSWORD = f.readline().strip()

notifier = IrssiNotifier(API_KEY, PASSWORD)
while True:
    with open('~/domains/my.kix.co.il/rpi-last.txt', 'r') as f:
        try:
            timestamp = float(f.read().strip())
            delta = time() - timestamp
            if delta > 60*5:
                notifier.send_message("i've stopped working", "#maia", "boiler")
        except ValueError:
            pass
    sleep(15)
