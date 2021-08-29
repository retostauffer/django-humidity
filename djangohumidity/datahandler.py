

from django.conf import settings
from datetime import datetime as dt

import json
from .models import *

def get_data(sensor_id, param_id):

    # Loading the parameter object
    param = Sensor.objects.get(id = sensor_id).parameter_set.all().get(id = param_id)

    values    = []
    datetime  = []
    for rec in param.data_set.all():
        values.append(rec.data_value)
        datetime.append(rec.data_datetime.isoformat())

    res = dict(datetime = datetime, value = values)

    return res
