from django.db import models
from django.contrib.auth.models import User

class OfferedService(models.Model):
    service_type = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    


   
    
class TemperatureData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    temperature = models.FloatField(default=0.0)
    humidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user.username}, Temp: {self.temperature}°C, Humidity: {self.humidity}%"



class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(OfferedService, on_delete=models.CASCADE)
    subscription_duration = models.CharField(max_length=100)
    interval_between_readings = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    

