from django.db import models
from django.utils import timezone


class Log(models.Model):
    device = models.TextField()
    gas = models.DecimalField(max_digits=20, decimal_places=2)
    dust = models.DecimalField(max_digits=20, decimal_places=2)
    temperature = models.DecimalField(max_digits=20, decimal_places=2)
    humidity = models.DecimalField(max_digits=20, decimal_places=2)
    created_date = models.DateTimeField(default=timezone.now)
