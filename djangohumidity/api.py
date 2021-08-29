

from django.conf import settings
from django.shortcuts import HttpResponse
from datetime import datetime as dt

import json
import re

from .models import *

def store(request):
    """

    Requires the following inputs:
    - key: access key (secret)
    - sensor: name of the sensor
    - param: name of the parameter
    - timestamp: integer time stamp
    - value: float value

    If not available the script will throw an error.
    Else the key is checked and we try to insert the data into
    the database.

    Error handling could be nicer.
    """

    args = request.GET
    error = False # Set non-bool once we encounter a problem.
    required = ["key", "sensor", "param", "timestamp", "value"]

    for req in required:
        if not req in args:
            error = "Missing \"{:s}\" on input.".format(req)

    # Checking key
    if not error and not args["key"] in settings.API_KEYS:
        error = "Error: \"{:s}\" is an invalid API key.".format(args["key"])

    # Processing data
    if not error:

        # Checking if all arguments are valid
        try:
            timestamp = int(args["timestamp"])
        except:
            raise ValueError("timestamp cannot be converted to integer.")

        try:
            value = float(args["value"])
        except:
            raise ValueError("timestamp cannot be converted to integer.")

        # Find sensor and parameter
        sens = Sensor.objects.get(sensor_name = args["sensor"])
        if not sens:
            raise ValueError("Sensor \"{:s}\" not found.".format(args["sensor"]))

        param = sens.parameter_set.all().get(param_name = args["param"])
        if not param:
            raise ValueError("No parameter \"{:s}\" for sensor \"{:s}\" found.".format(
                            args["param"], args["sensor"]))

        # Store data
        param.data_set.update_or_create(defaults = dict(data_value = value),
                                        data_datetime = dt.fromtimestamp(timestamp))



    if error:
        res = error
    else:
        res = json.dumps(args)

    content_type = "text"
    return HttpResponse(res, content_type = content_type) if request else res
