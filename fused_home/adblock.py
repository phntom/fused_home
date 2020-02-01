from collections import Counter

import requests
from tldextract import tldextract

URLS = (
    'https://raw.githubusercontent.com/tarampampam/static/master/hosts/block_shit.txt',
    'https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts;showintro=0',
    'https://adaway.org/hosts.txt',
)

WHITE_LIST_TOP_LEVEL = {
    'akamaiedge.net',
    'akamaitechnologies.com',
    'youtube.com',
    'google.com',
    'googlevideo.com',
    'youtube-nocookie.com',
    'edgesuite.net',
    'skype.com',
    'apis.google.com',
    'amazonaws.com',
    'assoc-amazon.com',
    'i1.ytimg.com',
}


def download_all():
    for num, url in enumerate(URLS):
        result = requests.get(url)
        result.raise_for_status()
        with open(f'ads_{num}.txt', 'w+') as w:
            w.write(result.content.decode('UTF-8'))


def get_hosts_set():
    for num in range(len(URLS)):
        with open(f'ads_{num}.txt') as f:
            for line in f:
                if '127.0.0.1' not in line:
                    continue
                yield tldextract.extract(line.strip().split(' ')[1])


def aggregate_domains():
    counter = Counter()
    yielded = set()
    for host in get_hosts_set():
        top_level = f'{host.domain}.{host.suffix}'
        counter[top_level] += 1
    for host in get_hosts_set():
        top_level = f'{host.domain}.{host.suffix}'
        if top_level in yielded:
            continue
        if host.subdomain:
            if counter[top_level] <= 5 or top_level in WHITE_LIST_TOP_LEVEL:
                yield f'{host.subdomain}.{host.domain}.{host.suffix}'
            else:
                yielded.add(top_level)
                yield f'*{top_level}'
        elif top_level in WHITE_LIST_TOP_LEVEL:
            continue
        else:
            yielded.add(top_level)
            yield f'*{top_level}'


if __name__ == '__main__':
    download_all()
    for x in range(6, 999):
        print(f"remove {x}")
    for x in aggregate_domains():
        print(f'add chain=prerouting protocol=tcp dst-port=443 in-interface=bridge connection-mark=no-mark '
              f'tls-host="{x}" action=jump jump-target=ads-list comment="tls-host={x}"')

"""
 0  D ;;; special dummy rule to show fasttrack counters
      chain=prerouting action=passthrough

 1  D ;;; special dummy rule to show fasttrack counters
      chain=forward action=passthrough

 2  D ;;; special dummy rule to show fasttrack counters
      chain=postrouting action=passthrough

 3    chain=ads-list action=add-dst-to-address-list address-list=list-ads
      address-list-timeout=12h log=no log-prefix=""

 4    chain=ads-list action=mark-connection new-connection-mark=mark-ads
      passthrough=yes dst-address-list=list-ads connection-mark=no-mark
      in-interface-list=LAN log=no log-prefix=""

 5    chain=ads-list action=mark-routing new-routing-mark=route-ads
      passthrough=no connection-mark=mark-ads log=no log-prefix=""

 6    ;;; tls-host=*doubleclick.net
      chain=prerouting action=jump jump-target=ads-list protocol=tcp
      connection-mark=no-mark in-interface=bridge dst-port=443

"""
