


from djangohumidity.models import *
from django.shortcuts import render

# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def home(request):

    context = dict(author = "reto")

    return render(request, "index.html", context)


# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
def dataview(request, sensor_id, param_id):

    from .datahandler import get_data

    # Loading all available sensors and defined parameters
    # for the navigation part.
    sensors = []
    for sens in Sensor.objects.all():
        params = []
        for par in sens.parameter_set.all():
            params.append(dict(id = par.id, name = par.param_name))
        sensors.append(dict(sensor = dict(id = sens.id, type = sens.sensor_type, name = sens.sensor_name),
                            parameter = params))


    data = get_data(sensor_id, param_id)

    context = dict(data = data, sensors = sensors)
    return render(request, "dataview.html", context)


# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
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











