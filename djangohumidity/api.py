

from django.conf import settings
from django.shortcuts import HttpResponse
from datetime import datetime as dt
from django.utils.timezone import make_aware

import json
import re

import logging
logger = logging.getLogger()

from .models import *

from django.views.decorators.cache import never_cache

@never_cache
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

        error = []

        # Checking if all arguments are valid
        try:
            timestamp = int(args["timestamp"])
        except:
            error.append("timestamp cannot be converted into integer")

        try:
            value = float(args["value"])
        except:
            error.append("value cannot be converted to float")

        # Find sensor and parameter
        sens = Sensor.objects.get(sensor_name__exact = args["sensor"])
        if not sens:
            error.append("Sensor \"{:s}\" not found.".format(args["sensor"]))

        param = sens.parameter_set.get(param_name__exact = args["param"])
        if not param:
            error.append("No parameter \"{:s}\" for sensor \"{:s}\" found.".format(
                            args["param"], args["sensor"]))

        # Store data
        if len(error) == 0:
            param.data_set.update_or_create(defaults = dict(data_value = value),
                                            data_datetime = make_aware(dt.fromtimestamp(timestamp)))
        else:
            error = dict(error = error)



    if error:
        res = error
    else:
        res = json.dumps(args)

    content_type = "text"
    return HttpResponse(res, content_type = content_type) if request else res
