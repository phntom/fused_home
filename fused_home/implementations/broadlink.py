from dataclasses import field

from interfaces.connection import HostPort
from interfaces.sensor import AirQuality, Noise, Lux, Thermometer


class A1(AirQuality, Noise, Lux, Thermometer):
    host_port: HostPort = field(default=HostPort)

