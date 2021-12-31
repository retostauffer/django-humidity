


from django.db import models

class Sensor(models.Model):

    # Sensors (basically piece of hardware)
    sensor_name = models.CharField(max_length = 15, unique = True, null = False)
    sensor_type = models.CharField(max_length = 15, null = False)
    sensor_desc = models.CharField(max_length = 100, null = True)
    sensor_color = models.CharField(max_length = 9, null = False)

    def __str__(self):

        x  = "  Sensor {:d}\n".format(self.id)
        x += "      Sensor name:   {:s}\n".format(self.sensor_name)
        x += "      Sensor type:   {:s}\n".format(self.sensor_type)
        x += "      Sensor color:  {:s}\n".format(self.sensor_color)
        return x

class Parameter(models.Model):

    # Linking parameters to sensors
    param_sensor   = models.ForeignKey(Sensor, on_delete = models.CASCADE)
    param_name     = models.CharField(max_length = 15, null = False)

    def __str__(self):

        x  = "  Parameter {:d}\n".format(self.id)
        x += "      Sensor:       {:s} ({:s}, {:d})\n".format(self.param_sensor.sensor_name,
                                                              self.param_sensor.sensor_type,
                                                              self.param_sensor.id)
        x += "      Name:         {:s}\n".format(self.param_name)
        return x

class Data(models.Model):

    # Table where we store the observed values. Linked
    # to Parameter > Sensor
    data_datetime  = models.DateTimeField() #IntegerField(null = False)
    data_param     = models.ForeignKey(Parameter, on_delete = models.CASCADE)
    data_value     = models.FloatField()

    class Meta:
            unique_together = (("data_datetime", "data_param_id"))

    def __str__(self):

        x  = "  Data object:\n"
        x += "       Datetime:  {:s}\n".format(str(self.data_datetime))
        x += "       Value:     {:10.5f}\n".format(self.data_value)
        return x
