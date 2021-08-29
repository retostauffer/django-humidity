#!/usr/bin/python3

import board
from adafruit_dht import DHT11
from time import sleep
import datetime
import sys

# Setting up the sensors
SENSORS = {"Sensor_1": DHT11(board.D18),
           "Sensor_2": DHT11(board.D17),
           "Sensor_3": DHT11(board.D27),
           "Sensor_4": DHT11(board.D22)}

# Number of trys when getting an NA reading
NTRY = 4

current = {}
for sensor_name,obj in SENSORS.items():

    attempt = 0
    while attempt < NTRY:
        attempt += 1
        print("   Reading \"{:s}\" now".format(sensor_name))
        try:
            obj.measure()
            t = sens.temperature
            r = sens.humidity
            print("         Temperature:   {:d}".format(t))
            print("         Rel. humidity: {:d}".format(t)
            break
        except RuntimeError:
            print("         Reading failed, eventually repeat ...")





