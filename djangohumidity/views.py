


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

    from .datahandler import get_data

    # Prepare the data 
    temp = []

    sensors = Sensor.objects.all()

    # Prepare temeprature data
    temperature = []
    for sens in sensors:
        try:
            p = sens.parameter_set.get(param_name = "temperature")
        except:
            continue

        # Prepare the object for plotly.js
        tmp = get_data(sens.id, p.id)
        tmp = dict(type = "scatter", mode = "lines", name = sens.sensor_name,
                   x = tmp["datetime"], y = tmp["value"],
                   line = dict(color = sens.sensor_color))
        temperature.append(tmp)

    # Prepare temeprature data
    humidity = []
    for sens in sensors:
        try:
            p = sens.parameter_set.get(param_name = "humidity")
        except:
            continue

        # Prepare the object for plotly.js
        tmp = get_data(sens.id, p.id)
        tmp = dict(type = "scatter", mode = "lines", name = sens.sensor_name,
                   x = tmp["datetime"], y = tmp["value"],
                   line = dict(color = sens.sensor_color))
        humidity.append(tmp)

    context = dict(temperature = temperature, humidity = humidity)
    return render(request, "all.html", context)











