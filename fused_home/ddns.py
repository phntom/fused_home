#!/usr/bin/python3
#
# Easy Python3 Dynamic DNS
# By Jed Smith <jed@jedsmith.org> 4/29/2009
# This code and associated documentation is released into the public domain.
#
# This script **REQUIRES** Python 3.0 or above.  Python 2.6 may work.
# To see what version you are using, run this:
#
#   python --version
#
# To use:
#
#   0. You'll probably have to edit the shebang above.
#
#   1. In the Linode DNS manager, edit your zone (must be master) and create
#      an A record for your home computer.  You can name it whatever you like;
#      I call mine 'home'.  Fill in 0.0.0.0 for the IP.
#
#   2. Save it.
#
#   3. Go back and edit the A record you just created. Make a note of the
#      ResourceID in the URI of the page while editing the record.
#
#   4. Edit the four configuration options below, following the directions for
#      each.  As this is a quick hack, it assumes everything goes right.
#
# First, the resource ID that contains the 'home' record you created above. If
# the URI while editing that A record looks like this:
#
#  linode.com/members/dns/resource_aud.cfm?DomainID=98765&ResourceID=123456
#  You want 123456. The API key MUST have write access to this resource ID.
#
# As of lately ( 5/2016 ) the DOMAINID is not in the URI
# https://manager.linode.com/dns/resource/domain.com?id=000000
#                                          Resource ID  ^
#
import json
import logging
from os.path import expanduser
from time import sleep, time
from json import load
from urllib.parse import urlencode
from urllib.request import urlretrieve

from routeros_api import RouterOsApiPool

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=expanduser(f'~/logs/ddns2.log'),
                    filemode='a+',
                    )

RESOURCE4 = "6363291"
RESOURCE6 = "6363291"
#
#
# Find this domain by going to the DNS Manager in Linode and then clicking
# check next to the domain associates with the above resource ID.
# Number should be sitting in parentheses next to domain name.
#
#
DOMAIN = "114584"
#
# Your Linode API key.  You can generate this by going to your profile in the
# Linode manager.  It should be fairly long.
#
with open(expanduser("~/.linode.key")) as f:
    KEY = f.read().strip()
#
# The URI of a Web service that returns your IP address as plaintext.  You are
# welcome to leave this at the default value and use mine.  If you want to run
# your own, the source code of that script is:
#
#     <?php
#     header("Content-type: text/plain");
#     printf("%s", $_SERVER["REMOTE_ADDR"]);
#
with open(expanduser('~/.router.key')) as f:
    ROUTER_KEY = json.load(f)
    ROUTER_KEY.pop('MODEM_PASSWORD')
router_api = RouterOsApiPool(**ROUTER_KEY).get_api()
results = router_api.get_resource('/ip/address').get(interface='pppoe-out1')
address_v4 = results[0]['address'].split('/')[0] if results else None

GETIP = "https://a248.e.akamai.net/whatismyip.akamai.com/"
GETIP6 = "http://ip6only.me/api/"
#
# If for some reason the API URI changes, or you wish to send requests to a
# different URI for debugging reasons, edit this.  {0} will be replaced with the
# API key set above, and & will be added automatically for parameters.
#
API = "https://api.linode.com/api/?api_key={0}&resultFormat=JSON"
#
# Comment or remove this line to indicate that you edited the options above.
#
# exit("Did you edit the options?  vi this file open.")
#
# That's it!
#
# Now run dyndns.py manually, or add it to cron, or whatever.  You can even have
# multiple copies of the script doing different zones.
#
# For automated processing, this script will always print EXACTLY one line, and
# will also communicate via a return code.  The return codes are:
#
#    0 - No need to update, A record matches my public IP
#    1 - Updated record
#    2 - Some kind of error or exception occurred
#
# The script will also output one line that starts with either OK or FAIL.  If
# an update was necessary, OK will have extra information after it.
#
# If you want to see responses for troubleshooting, set this:
#
DEBUG = False


#####################
# STOP EDITING HERE #

def execute(action, parameters):
    # Execute a query and return a Python dictionary.
    uri = "{}&api_action={}".format(API.format(KEY), action)
    if parameters and len(parameters) > 0:
        uri = "{}&{}".format(uri, urlencode(parameters))
    if DEBUG:
        print("-->", uri)
    file, headers = urlretrieve(uri)
    if DEBUG:
        print("<--", file)
        print(headers, end="")
        print(open(file).read())
        print()
    json = load(open(file), encoding="utf-8")
    if len(json["ERRORARRAY"]) > 0:
        err = json["ERRORARRAY"][0]
        raise Exception("Error {0}: {1}".format(int(err["ERRORCODE"]),
                                                err["ERRORMESSAGE"]))
    return load(open(file), encoding="utf-8")


def ip():
    if address_v4:
        return address_v4
    file, headers = urlretrieve(GETIP)
    return open(file).read().strip()


def ip6():
    file, headers = urlretrieve(GETIP6)
    return open(file).read().split(',')[1]


def main():
    try:
        public4 = ip()
        public6 = ip6()
        for public, RESOURCE in ((public4, RESOURCE4), (public6, RESOURCE6)):
            res = execute("domain.resource.list", {"DomainID": DOMAIN, "ResourceID": RESOURCE})["DATA"]
            res = res[0]  # Turn res from a list to a dict
            if (len(res)) == 0:
                raise Exception("No such resource?".format(RESOURCE))

            with open(expanduser('~/ddns.last'), 'w') as w:
                w.write(str(time()))
            if res["TARGET"] != public:
                old = res["TARGET"]
                request = {
                    "ResourceID": res["RESOURCEID"],
                    "DomainID": res["DOMAINID"],
                    "Name": res["NAME"],
                    "Type": res["TYPE"],
                    "Target": public,
                    "TTL_Sec": res["TTL_SEC"]
                }
                execute("domain.resource.update", request)
                logging.info(f"updated {RESOURCE} ip address from {old} to {public}")
            return 1
        else:
            return 0
    except Exception:
        logging.exception("failed to update")
        return 2


if __name__ == "__main__":
    while True:
        main()
        sleep(30)
