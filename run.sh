#!/usr/bin/env sh
mkdir -p ~/logs
touch ~/logs/boiler_watchdog.log
python3 fused_home/boiler_watchdog.py &
python3 fused_home/ddns.py &

while true; do
    ps aux | grep -q boiler_watchdog.py || exit 1
    ps aux | grep -q ddns.py || exit 2
    sleep 60
done
