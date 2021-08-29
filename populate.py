

from djangohumidity.models import *
from datetime import datetime as dt

from django.conf import settings
from django.utils.timezone import make_aware

SENSORS = {"Sensor 1": "DHT11", "Sensor 2": "DHT11", "Sensor 3": "DHT11", "Sensor 4": "DHT11"}
PARAMS  = ["temperature", "humidity"]

import re

colors = ["#BB872D", "#46A347", "#00A6B6", "#A47FD9"]

for key,val in SENSORS.items():
    key = key.replace(" ", "_")

    # Get the 'id' from the name for the color
    tmp = int(re.findall("[0-9]+$", key)[0]) - 1

    sens = Sensor(sensor_name = key, sensor_type = val, sensor_color = colors[tmp])
    sens.save()


    for par in PARAMS:
        p = sens.parameter_set.create(param_name = par)
    #    tmp = make_aware(dt.fromtimestamp(1111111))
    #    p.data_set.update_or_create(defaults = {"data_value": 145.99}, data_datetime = tmp)
    #    p.data_set.update_or_create(defaults = {"data_value": 999.33}, data_datetime = tmp)



import pandas as pd
data = pd.read_csv("~/Downloads/test.log", sep = ";")
data = data.rename(columns = lambda x: x.strip())

print(data)


config = dict(s1_t  = ("Sensor_1", "temperature"),
              s1_rh = ("Sensor_1", "humidity"),
              s2_t  = ("Sensor_2", "temperature"),
              s2_rh = ("Sensor_2", "humidity"),
              s3_t  = ("Sensor_3", "temperature"),
              s3_rh = ("Sensor_3", "humidity"),
              s4_t  = ("Sensor_4", "temperature"),
              s4_rh = ("Sensor_4", "humidity"))

for key,vals in config.items():
    sens = Sensor.objects.get(sensor_name = vals[0])
    par  = sens.parameter_set.all().get(param_name = vals[1])

    print(sens)
    print(par)

    tmp = []
    for idx, row in data.iterrows():
        if row[key].strip() == "NA": continue
        tmp.append(Data(data_datetime = make_aware(dt.fromtimestamp(row["timestamp"])),
                        data_value    = row[key],
                        data_param    = par))

    tmp = Data.objects.bulk_create(tmp)



