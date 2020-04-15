#!/usr/bin/env sh
mkdir -p ~/logs
touch ~/logs/boiler_watchdog.log
export EXTERNAL_INTERFACE=eth1
python3 fused_home/boiler_watchdog.py &
python3 fused_home/ddns.py &
python3 fused_home/lights.py &
python3 fused_home/sensors.py &
python3 fused_home/hotbox.py &

while true; do
    ps aux | grep -q boiler_watchdog.py || exit 1
    ps aux | grep -q ddns.py || exit 2
    ps aux | grep -q lights.py || exit 3
    ps aux | grep -q sensors.py || exit 4
    ps aux | grep -q hotbox.py || exit 5
    sleep 60
done
