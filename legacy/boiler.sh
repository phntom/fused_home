#!/usr/bin/env bash

while true; do
        ./check_boiler.py
        if [[ $? -eq 200 ]]; then
#               echo boiler is on, waiting 15 minutes and tuning it off
                for i in {1..15}; do
                        sleep 60
                        ./check_boiler.py
                        if [[ $? -eq 204 ]]; then
#                               echo boiler is off before 15 minute mark
                                break
                        fi
                done
#               echo turning boiler off...
                ./turn_off_boiler.py
        fi
        sleep 30
done
