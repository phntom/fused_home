#!/usr/bin/env sh
mkdir -p ~/logs
touch ~/logs/boiler_watchdog.log
export EXTERNAL_INTERFACE=eth1
python3 fused_home/boiler_watchdog.py &
python3 fused_home/ddns.py &
python3 fused_home/lights.py &

while true; do
    ps aux | grep -q boiler_watchdog.py || exit 1
    ps aux | grep -q ddns.py || exit 2
    ps aux | grep -q lights.py || exit 3
    sleep 60
done
