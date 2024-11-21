from django.db import models
from django.contrib.auth.models import User

class OfferedService(models.Model):
    service_type = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    


   
    
class TemperatureData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    data = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)



class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(OfferedService, on_delete=models.CASCADE)
    subscription_duration = models.CharField(max_length=100)
    interval_between_readings = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    

