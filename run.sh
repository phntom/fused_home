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
    sleep 60
    [ `pgrep python3 | wc -l` -eq 5 ] || exit 1
done
