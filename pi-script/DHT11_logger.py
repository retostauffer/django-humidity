#!/usr/bin/python3

import board
from adafruit_dht import DHT11
from time import sleep
from datetime import datetime as dt
import sys

# Setting up the sensors
SENSORS = {"Sensor_1": DHT11(board.D18),
           "Sensor_2": DHT11(board.D17),
           "Sensor_3": DHT11(board.D27),
           "Sensor_4": DHT11(board.D22)}

# Number of trys when getting an NA reading
NTRY = 4

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def send_data(sensor, param, timestamp, value, BASEURL = "https://hum.retostauffer.org/api/store"):
    """
    Args
    ====
    sensor : str
        Name of the sensor (as in DB)
    param : str
        Name of the parameter (as in DB)
    timestamp : int
        Current time stamp; full seconds
    value : int
        Current measurement

    Return
    ======
    Returns an URL which is then called to store the value.
    """

    data = dict(key = "kd3489135aaDF",
                sensor    = sensor,
                param     = param,
                timestamp = timestamp,
                value     = value)

    from urllib import request, parse
    args = []
    for key,val in data.items(): args.append("{:s}={:s}".format(key, "{:d}".format(val) if isinstance(val, int) else val))
    url = "{:s}?{:s}".format(BASEURL, "&".join(args))
    print(url)
    response = request.urlopen(url)
    return response.read()


# -------------------------------------------------------------------
# --------------------------------------------------------------------
current = {}
for sensor_name,obj in SENSORS.items():

    attempt = 0
    t = None
    r = None
    print("   Reading \"{:s}\" now".format(sensor_name))
    while attempt < NTRY:
        attempt += 1
        try:
            obj.measure()
            timestamp = int(dt.now().timestamp())
            t = obj.temperature
            r = obj.humidity
            print("         Temperature:   {:d}".format(t))
            print("         Rel. humidity: {:d}".format(r))
            break
        except RuntimeError:
            print("         Reading failed, eventually repeat ...")


    # If we got some values
    if not t is None:
        content = send_data(sensor_name, "temperature", timestamp, t)
        print(content)

    if not r is None:
        content = send_data(sensor_name, "temperature", timestamp, t)
        print(content)




