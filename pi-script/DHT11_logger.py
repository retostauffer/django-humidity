#!/usr/bin/env python3
# --------------------------------------------------------------------
# Looping over a set of pre-defined sensors; reading parameters and
# store them using the corresponding api/store endpoint on my server.
#
# This script will be triggered once a minute on the raspberry. To
# avoid storing too many useless data the following is done:
# - Ever time we send data we store the time stamp and the current
#   value (for a specific sensor and parameter) in a file
# - If such a file already exists and is not older than 15 minutes:
#   - Do not send current value
# - Else send and write new timestamp/value into the temp file 
#   (overwrite if necessary)
# --------------------------------------------------------------------

import os
import sys
import argparse

import Adafruit_DHT as AD
from configparser import ConfigParser
from datetime import datetime as dt


# Setting up the sensors
SENSORS = {"Sensor_1": dict(pin = 18, type = AD.DHT11),
           "Sensor_2": dict(pin = 17, type = AD.DHT11),
           "Sensor_3": dict(pin = 27, type = AD.DHT11),
           "Sensor_4": dict(pin = 22, type = AD.DHT11)}

# Number of trys when getting an NA reading
NTRY = 4

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def send_data(value, timestamp, cache, apikey, force = False,
              BASEURL = "https://hum.retostauffer.org/api/store"):
    """
    Args
    ====
    value : int or float
        Current measurement
    timestamp : int
        Current time stamp; full seconds
    cache : DataCacheFile
        Object for handling data cache.
    apikey : str
        Secret api Key
    force : bool
        If set to True, the current value is sent no matter if it is the
        same as sent before.
    BASEURL : str
        URL of the API endpoint. Default set.

    Return
    ======
    Returns response from API.
    """

    if value is None:
        return "Value was None; don't process any further than this!"

    if not isinstance(value, int) or isinstance(value, float):
        raise TypeError("'value' must be integer or float")
    if not isinstance(timestamp, int):
        raise TypeError("'timestamp' must be integer")
    if not isinstance(cache, DataCacheFile):
        raise TypeError("'cache' must be of class DataCacheFile")
    assert isinstance(force, bool), TypeError("argument 'force' must be boolean")

    data = dict(key       = apikey,
                sensor    = cache.get("sensor_name"),
                param     = cache.get("param"),
                timestamp = timestamp,
                value     = value)

    # Let us first check if we have to send data.
    # We only send data if the current value is not the same
    # as cache.get("last_value"). "last_value" is None if we 
    # have no cache file or the cache file is too old.
    if force or (not cache.get("last_value") or abs(value - cache.get("last_value")) > 0.001):
        from urllib import request, parse
        args = []
        #print(data)
        for key,val in data.items():
            args.append("{:s}={:s}".format(key, "{:d}".format(val) if isinstance(val, int) else val))
        url = "{:s}?{:s}".format(BASEURL, "&".join(args))

        response = request.urlopen(url)
        res = response.read()

        # Store new (latest) value
        with open(cache.get("file"), "w") as fid: fid.write(f"{value}")

    else:
        res = {"info": "No need to send current data."}
    return res


# --------------------------------------------------------------
# Small helper class to handle DataCacheFiles
# --------------------------------------------------------------
class DataCacheFile:

    def __init__(self, sensor_name, param, maxage = 15 * 60):
        """DataCacheFile(sensor_name, param, maxage = 15 * 60)

        Arguments
        =========
        sensor_name : str
            Name of the sensor
        param : str
            Parameter name
        maxage : int
            Maximum age (in seconds) of the last modification date
            of the file to be considered. If the file is older than that
            we will handle it as if it would not exist. Defaults to 15 minutes.

        Return
        ======
        No return, initializes class.
        """

        if not isinstance(sensor_name, str):  raise TypeError("'sensor_name' must be str")
        if not isinstance(param, str):        raise TypeError("'param' must be str")
        if not isinstance(maxage, int):       raise TypeError("'maxage' must be int")
        self._sensor_name = sensor_name
        self._param       = param
        self._maxage      = maxage
        self._file        = f"_{sensor_name}_{param}"
        self._file_age    = self._get_file_age_()
        self._last_value  = self._get_last_value_()


    def _get_file_age_(self):
        import os
        import datetime as dt
        file = self.get("file")
        if os.path.isfile(file):
            file_age = int(dt.datetime.now().timestamp() - os.stat(file).st_mtime)
        else:
            file_age = None
        return file_age

    def _get_last_value_(self):
        import os

        file     = self.get("file")
        file_age = self.get("file_age")

        # File does not exist or file_age is None: return None
        if not os.path.isfile(file) or not file_age:
            res = None
        # Else if file_age > maxage: return None
        elif file_age > self.get("maxage"):
            res = None
        # Else we try to read the file
        else:
            print(f"    Trying to read last value from {file}")
            # Try to read file. If not possible - set res to None
            try:
                with open(file, "r") as fid:
                    res = fid.readline()
                    res = float(res)
            except:
                res = None

        return res



    def get(self, what):
        """get(what)

        Arguments
        =========
        what : str
            The property to get. E.g., if 'what = "file"' the function
            will return property "_file" if it exists, or 'None' else.

        Return
        ======
        str or None: Property if it exists, else None.
        """
        if not isinstance(what, str):
            raise TypeError("'what' must be str")
        if hasattr(self, f"_{what}"): res = getattr(self, f"_{what}")
        else:                         res = None
        return res


    def __repr__(self):
        res  = "    DataCacheFile(\"{:s}\", \"{:s}\")\n".format(self.get("sensor_name"), self.get("param"))
        res += "        Filename:    {:s}\n".format(self.get("file"))
        res += "        File exists: {:s}\n".format(str(os.path.isfile(self.get("file"))))
        res += "        Last value:  {:s}\n".format("----" if not self.get("last_value") else "{:.3f}".format(self.get("last_value")))
        return res


# -------------------------------------------------------------------
# --------------------------------------------------------------------
if __name__ == "__main__":


    parser = argparse.ArgumentParser(description = "Some options I use to play around")
    parser.add_argument("-f", "--force", action = "store_true",
            help = "If set, force submission of reading even if the value has not changed within the last couple of minutes.")
    parser.add_argument("-p", "--pins", metavar = "pins",
            type = int, nargs = "+", default = [18, 17, 27, 22],
            help = "GPIO pins to be read (if defined as sensors)")
    args = parser.parse_args()

    # Loading API key
    CNF = ConfigParser()
    CNF.read("../my.cnf")
    apikey = CNF.get("config", "API_KEY")

    current = {}

    for sname,sconfig in SENSORS.items():
        if not sconfig["pin"] in args.pins:
            print(f"   Skipping pin {sconfig['pin']}, not in -p/--pins args (or default; {args.pins=}")
            continue

        print(f"   Reading \"{sname}\"")

        # Our files to cache/store latest obs
        cache = {}
        for param in ["temperature", "humidity"]:
            cache[param] = DataCacheFile(sname, param)

        [r,t] = AD.read_retry(sconfig["type"], sconfig["pin"])
        if not r or not t:
            print(f"    No/bad reading from {sname}, skip")
            continue

        timestamp = int(dt.now().timestamp())
        print(f"         Temperature:   {t}")
        print(f"         Rel. humidity: {r}")
    
        content = send_data(int(t), timestamp, cache["temperature"], apikey, args.force)
        print(content)
        content = send_data(int(r), timestamp, cache["humidity"], apikey, args.force)
        print(content)

        del t, r

