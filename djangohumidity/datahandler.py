

from django.utils.timezone import make_aware
from django.conf import settings
import datetime as dt

import json
from .models import *

def get_data(sensor_id, param_id, ndays = 7):

    if not isinstance(ndays, int):
        raise TypeError("ndays must be integer")
    if ndays < 1:
        raise TypeError("ndays must be larger than 0")

    # Starting timestamp
    now   = dt.datetime.now()
    start = make_aware(now - dt.timedelta(ndays))

    # Loading the parameter object
    param = Sensor.objects.get(id = sensor_id).parameter_set.get(id = param_id)
    print(param)

    values    = []
    datetime  = []
    #for rec in param.data_set.all():
    for rec in param.data_set.filter(data_datetime__gte = start):
        values.append(rec.data_value)
        datetime.append(rec.data_datetime.isoformat())

    res = dict(datetime = datetime, value = values)

    return res
