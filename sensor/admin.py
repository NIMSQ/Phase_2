from django.contrib import admin
from .models import OfferedService, TemperatureData, Subscription

admin.site.register(OfferedService)
admin.site.register(TemperatureData)
admin.site.register(Subscription)