

from django.conf import settings
from django.shortcuts import HttpResponse
import datetime as dt
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
                                            data_datetime = make_aware(dt.datetime.fromtimestamp(timestamp)))
        else:
            error = dict(error = error)



    if error:
        res = error
    else:
        res = json.dumps(args)

    content_type = "text"
    return HttpResponse(res, content_type = content_type) if request else res


# simple magnus equation; parmaeters Sonntag 1990
def dewpoint(t, rh):
    """dewpoint(t, rh)

    Calculate dew point temperature via magnus equation.
    """
    from numpy import log, round
    t = t + 273.15
    return round(log(rh / 100.) + (17.62 * t) / (243.12 + t), 1)

# --------------------------------------------------------------------
# --------------------------------------------------------------------
def get_sensors():
    """get_sensors()

    Returns
    =======
    Returns a dictionary with all available sensors.
    Used by different api calls/views.
    """
    sensors = []
    for sens in Sensor.objects.all():
        params = []
        for par in sens.parameter_set.all():
            params.append(dict(id = par.id, name = par.param_name))
        sensors.append(dict(sensor = dict(id = sens.id, type = sens.sensor_type, name = sens.sensor_name),
                            parameter = params))
    return sensors


# --------------------------------------------------------------------
# --------------------------------------------------------------------
def get_data(sensor_id, param_id, ndays = 7, isoformat = True):
    """get_data(sensor_id, param_id, ndays = 7)

    Arguments
    =========
    sensor_id : int
        ID of the sensor to fetch data for.
    param_id : int
        ID of the parameter to fetch data for.
    ndays : int
        How many days back the data should be fetched, defaults to 7.
    isoformat : bool
        Should the date be returned in the javascript iso format or not?
        If 'isoformat = True' a string will be returned, else the timestamp
        as integer. Defaults to True.

    Returns
    =======
    dict : Dictionary containing two vectors with 'datetime' and corresponding
    observed value for this sensor/parameter.
    """

    if not isinstance(sensor_id, int):
        raise TypeError("'sensor_id' must be integer")
    if not isinstance(param_id, int):
        raise TypeError("'param_id' must be integer")
    if not isinstance(ndays, int):
        raise TypeError("ndays must be integer")
    if ndays < 1:
        raise TypeError("ndays must be larger than 0")
    if not isinstance(isoformat, bool):
        raise TypeError("'isoformat' must be logical True or False")

    # Starting timestamp
    now   = dt.datetime.now()
    start = make_aware(now - dt.timedelta(ndays))

    # Loading the parameter object
    param = Sensor.objects.get(id = sensor_id).parameter_set.get(id = param_id)

    values    = []
    datetime  = []
    for rec in param.data_set.filter(data_datetime__gte = start):
        values.append(rec.data_value)
        if isoformat:
            datetime.append(rec.data_datetime.isoformat())
        else:
            datetime.append(rec.data_datetime.timestamp())

    res = dict(datetime = datetime, value = values)

    return res


# --------------------------------------------------------------------
# --------------------------------------------------------------------
def get_data_dict(sensor_id, param_id, ndays = 7):
    """get_data_dict(sensor_id, param_id, ndays = 7)

    Arguments
    =========
    sensor_id : int
        ID of the sensor to fetch data for.
    param_id : int
        ID of the parameter to fetch data for.
    ndays : int
        How many days back the data should be fetched, defaults to 7.

    Returns
    =======
    dict : Dictionary with 'data' (datetime/observed value) for the
    current sensor and parameter, as well as 'sensors' containing all
    available sensors (used to generate some nav items).
    """

    from .api import get_data
    from .api import get_sensors

    # Loading all available sensors and defined parameters
    # for the navigation part.
    sensors = get_sensors()
    data    = get_data(sensor_id, param_id, ndays)
    context = dict(data = data, sensors = sensors)

    return context


# --------------------------------------------------------------------
# API VIEW
# --------------------------------------------------------------------
@never_cache
def data(request, ndays = 7):
    """data(request, ndays = 7)

    API endpoint for data view.

    Arguments
    =========
    ndays : int
        Number of days to load. Defaults to 7.
    """

    from json import dumps
    from .api import get_data
    from .api import dewpoint
    from .models import Parameter, Sensor
    import pandas as pd
    from numpy import floor, ceil

    parameters = Parameter.objects.all()
    #parameters = Parameter.objects.filter(param_name__exact = "temperature")

    data = []
    for param in parameters:
        key = f"{param.param_sensor.sensor_name}_{param.param_name}"
        tmp = get_data(param.param_sensor.id, param.id, isoformat = False)
        tmp = pd.DataFrame(tmp["value"], columns = [key],
                           index = pd.to_datetime(tmp["datetime"], unit = "s"))
        data.append(tmp)



    # Target temporal resolution; create and append a dummy
    # column to the data frame from the data itself. We then
    # use this to interpolate all data to the same temporal
    # resolution and only pick the 'target_index' time steps.
    target_index = pd.date_range(dt.datetime.fromtimestamp(60. * floor(min(tmp.index).timestamp() / 60.)),
                                 dt.datetime.fromtimestamp(60. * ceil(max(tmp.index).timestamp() / 60.)),
                                 freq = "30s")
    dummy = pd.DataFrame(dict(dummy = 1), index = target_index)
    data.append(dummy)

    data = pd.concat(data)
    data = data.sort_index().interpolate().round(1)

    data = data.loc[target_index,:]
    del data["dummy"]

    data = data.reset_index()
    data = data.rename(columns = {"index": "timestamp"})
    data.timestamp = [int(x.timestamp()) for x in data.timestamp]

    data["Sensor_1_dewpoint"] = dewpoint(data.Sensor_1_temperature, data.Sensor_1_humidity)

    res = data.tail().to_dict(orient = "list")

    return HttpResponse(dumps(res), content_type = "application/json")




