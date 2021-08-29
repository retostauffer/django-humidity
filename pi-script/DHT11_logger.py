#!/usr/bin/python3

import board
from adafruit_dht import DHT11
from time import sleep
import datetime
import sys

# Setting up the sensors
devs = {"s1": DHT11(board.D18),
        "s2": DHT11(board.D17),
        "s3": DHT11(board.D27),
        "s4": DHT11(board.D22)}


first = True

while True:
    current = {}
    for key,sens in devs.items():
        try:
            sens.measure()
            t = sens.temperature
            r = sens.humidity
            #print("Sensor {:s}:      {:d}     {:d}".format(key, t, r))
            current["{:s}_t".format(key)] = t
            current["{:s}_rh".format(key)] = r
        except RuntimeError:
            #print("Failed for this one ...")
            current["{:s}_t".format(key)] = "NA"
            current["{:s}_rh".format(key)] = "NA"

    # Printing header
    if first:
        header = ["timestamp"]
        for sens in devs:
            for val in ["t", "rh"]:
                key = "{:s}_{:s}".format(sens, val)
                header.append(key)
        print("; ".join(header))
        first = False

    # Print measurements
    # Start with fresh list solely
    # containing the timestamp as string.
    values = ["{:.0f}".format(datetime.datetime.now().timestamp())]
    for sens in devs:
        for val in ["t", "rh"]:
            key = "{:s}_{:s}".format(sens, val)
            val = current[key]
            if isinstance(val, int):
                val = "{:d}".format(val)

            values.append(val)

    print("; ".join(values))
    sys.stdout.flush()


    sleep(10)
