# Populating database for testing

import sys
import os
import re
import numpy as np

from djangohumidity.models import *
import datetime as dt

from django.conf import settings
from django.utils.timezone import make_aware

SENSORS = {"Sensor 1": "DHT11", "Sensor 2": "DHT11", "Sensor 3": "DHT11", "Sensor 4": "DHT11"}
PARAMS  = ["temperature", "humidity"]

colors = ["#BB872D", "#46A347", "#00A6B6", "#A47FD9"]

for key,val in SENSORS.items():
    key = key.replace(" ", "_")

    # Get the 'id' from the name for the color
    tmp = int(re.findall("[0-9]+$", key)[0]) - 1

    sens,created = Sensor.objects.get_or_create(sensor_name = key, sensor_type = val,
                                                sensor_color = colors[tmp])

    for par in PARAMS:
        p = sens.parameter_set.get_or_create(param_name = par)

print("Number of sensors: {:d}".format(len(Sensor.objects.all())))

# Filling in some random data
config = dict(s1_t  = ("Sensor_1", "temperature"),
              s1_rh = ("Sensor_1", "humidity"),
              s2_t  = ("Sensor_2", "temperature"),
              s2_rh = ("Sensor_2", "humidity"),
              s3_t  = ("Sensor_3", "temperature"),
              s3_rh = ("Sensor_3", "humidity"),
              s4_t  = ("Sensor_4", "temperature"),
              s4_rh = ("Sensor_4", "humidity"))
# Period to fill
start = dt.datetime.now() - dt.timedelta(.5)
end   = dt.datetime.now()

for key,vals in config.items():
    sens = Sensor.objects.get(sensor_name__exact = vals[0])
    par  = sens.parameter_set.all().get(param_name__exact = vals[1])

    # Getting random value
    if par.param_name == "temperature":
        def fn(): return float(np.round(np.random.uniform(14, 22, 1)))
    else:
        def fn(): return float(np.round(np.random.uniform(40, 60, 1)))


    print(sens)
    print(par)
    curr = start
    tmp = []
    while curr < end:
        curr = curr + dt.timedelta(0, int(np.random.randint(1, 100, 1)[0]))
        tmp.append(Data(data_datetime = make_aware(curr),
                        data_param    = par,
                        data_value    = fn()))

    tmp = Data.objects.bulk_create(tmp)



