


from djangohumidity.models import *
from django.shortcuts import render
from django.views.decorators.cache import never_cache


# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def home(request):

    context = dict(author = "reto")

    return render(request, "index.html", context)

# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
@never_cache
def dataview(request, sensor_id, param_id):

    from .api import get_data_dict

    context = get_data_dict(sensor_id, param_id)

    return render(request, "dataview.html", context)


# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
@never_cache
def dataall(request):

    import pandas as pd
    from .api import get_data
    from .api import dewpoint

    # Prepare the data 
    temp = []

    sensors = Sensor.objects.all()

    # Prepare temeprature data
    data_temperature = []
    data_humidity    = []
    data_dewpoint    = []
    for sens in sensors:

        # As we also calculate the dewpoint temperature we need
        # both, temperature and humidity. Not that nice but good for now.
        try:
            t  = sens.parameter_set.get(param_name = "temperature")
            rh = sens.parameter_set.get(param_name = "humidity")
        except:
            continue

        # Adding/preparing temperature for plotly.js
        tmp_t  = get_data(sens.id, t.id)
        tmp_t  = dict(type = "scatter", mode = "lines", name = sens.sensor_name,
                      x = tmp_t["datetime"], y = tmp_t["value"],
                      line = dict(color = sens.sensor_color))

        # Adding/preparing humidity for plotly.js
        tmp_rh = get_data(sens.id, rh.id)
        tmp_rh = dict(type = "scatter", mode = "lines", name = sens.sensor_name,
                   x = tmp_rh["datetime"], y = tmp_rh["value"],
                   line = dict(color = sens.sensor_color))

        # Creating pandas to calculate dewpoint temperature
        tmp_dp = pd.merge(pd.DataFrame(dict(t  = tmp_t["y"],  datetime = pd.to_datetime(tmp_t["x"]))),
                          pd.DataFrame(dict(rh = tmp_rh["y"], datetime = pd.to_datetime(tmp_rh["x"]))),
                          how = "outer",
                          on = "datetime")
        tmp_dp = tmp_dp.sort_values("datetime")
        tmp_dp = tmp_dp.interpolate(method = "ffill").dropna()
        tmp_dp["dewpoint"] = dewpoint(tmp_dp["t"], tmp_dp["rh"])
        tmp_dp = dict(type = "scatter", mode = "lines", name = sens.sensor_name,
                   x = [x.isoformat() for x in tmp_dp.datetime], y = [x for x in tmp_dp.dewpoint],
                   line = dict(color = sens.sensor_color))

        # Appending dew point temperature
        data_temperature.append(tmp_t)
        data_humidity.append(tmp_rh)
        data_dewpoint.append(tmp_dp)



    context = dict(temperature = data_temperature, humidity = data_humidity, dewpoint = data_dewpoint)
    return render(request, "all.html", context)











