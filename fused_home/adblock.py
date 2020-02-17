from collections import Counter

import requests
from tldextract import tldextract

URLS = (
    'https://raw.githubusercontent.com/tarampampam/static/master/hosts/block_shit.txt',
    'https://block.energized.pro/spark/formats/hosts.txt',
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
    'ytimg.com',
    'amazon.com',
    'instagram.com',
    'ynet.co.il',
    'spotify.com',
    'netflix.com',
    'github.com',
    'gmail.com',
    'energized.pro',
    'githubusercontent.com',
    'microsoft.com',
    'cloudfront.com',
    'facebook.com',
    'googleapis.com',
    'twitter.com',
    'linkedin.com',
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
                if line.startswith('#') or ('0.0.0.0' not in line and '127.0.0.1' not in line):
                    continue
                domain = line.strip().split(' ')[1]
                extracted = tldextract.extract(domain)
                if extracted.suffix:
                    yield extracted


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
            if top_level in WHITE_LIST_TOP_LEVEL: # counter[top_level] <= 5 or
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

    with open('remove-adblock.txt', 'w+') as fp:
        fp.write("/ip firewall mangle\n")
        fp.write("print value-list\n")
        for x in range(6, 10000):
            fp.write(f"remove {x}\n")
    download_all()
    fps = list(open(f'adblock{n}.txt', 'w+') for n in range(1))
    for n in range(len(fps)):
        fps[n].write("/ip firewall mangle\n")
    for n, x in enumerate(aggregate_domains()):
        fp = fps[n % len(fps)]
        fp.write(f'add chain=prerouting protocol=tcp dst-port=443 in-interface=bridge connection-mark=no-mark '
                 f'tls-host="{x}" action=jump jump-target=ads-list comment="tls-host={x}"\n')
    print("sftp admin@192.168.88.1")
    print("cd /disk1")
    print("put *adblock*txt")
    print("/execute /import disk1/remove-adblock.txt")
    print("/execute /import disk1/adblock0.txt")
"""
/ip firewall mangle
add action=add-dst-to-address-list address-list=list-ads address-list-timeout=12h chain=ads-list
add action=mark-connection chain=ads-list connection-mark=no-mark dst-address-list=list-ads in-interface-list=LAN \
    new-connection-mark=mark-ads passthrough=yes
add action=mark-routing chain=ads-list connection-mark=mark-ads new-routing-mark=route-ads passthrough=no
"""
