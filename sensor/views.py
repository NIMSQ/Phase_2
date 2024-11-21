# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import OfferedService, Subscription  # Assume OfferedService model is set up to store service details
import paho.mqtt.client as mqtt
from .models import TemperatureData
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Max, Min, Avg



@login_required
def my_subscriptions(request):
    # Filter subscriptions by the logged-in user
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'sensor/my_subscriptions.html', {'subscriptions': subscriptions})





def send_mqtt_notification(user_id, interval, duration, topic):
    """Sends an MQTT message to notify about a new subscription."""
    mqtt_broker = "192.168.100.112"  # Update with your MQTT broker IP
    mqtt_port = 1883
    client = mqtt.Client()
    
    # Attempt connection with logging
    try:
        print("Attempting to connect to MQTT broker...")
        client.connect(mqtt_broker, mqtt_port, 60)
        print("Connected to MQTT broker.")
        
        # Construct the message
        message = f"You have a new subscriber with user ID {user_id}. Publish the data every {interval} for {duration} to this topic {topic}."
        print(f"Publishing message: {message}")
        
        # Publish the message
        client.publish("sensor/subscriptions", message)
        print("Message published successfully.")
        
    except Exception as e:
        print(f"Failed to send MQTT message: {e}")
    finally:
        # Disconnect after publishing
        client.disconnect()
        print("Disconnected from MQTT broker.")
        
@login_required
def subscribe(request, service_id):
    if request.method == 'POST':
        print("Processing subscription...")
        subscription_duration = request.POST.get('subscription_duration')
        interval_between_readings = request.POST.get('interval_between_readings')
        user = request.user

        service = get_object_or_404(OfferedService, id=service_id)
        
        # Create a new Subscription object
        Subscription.objects.create(
            user=user,
            service=service,
            subscription_duration=subscription_duration,
            interval_between_readings=interval_between_readings
        )
        print("Subscription created in the database.")

        user_topic = f"sensor/{user.id}/temperature"
        
        # Send MQTT notification
        send_mqtt_notification(
            user_id=user.id,
            interval=interval_between_readings,
            duration=subscription_duration,
            topic=user_topic
        )

        # Add a success message for user feedback
        messages.success(request, "You have successfully subscribed to the service.")
        print("Subscription success message set.")
        
        return redirect('sensor:service_list')

    print("Redirecting back to service list without subscribing.")
    return redirect('sensor:service_list')

@login_required
def user_temperature_data(request):
    # Get the latest temperature data for the current user
    temperature_data = TemperatureData.objects.filter(user=request.user).order_by('-timestamp').first()

    # Calculate max, min, and average temperatures for the user
    max_temperature = TemperatureData.objects.filter(user=request.user).aggregate(Max('data'))['data__max']
    min_temperature = TemperatureData.objects.filter(user=request.user).aggregate(Min('data'))['data__min']
    avg_temperature = TemperatureData.objects.filter(user=request.user).aggregate(Avg('data'))['data__avg']

    # Adjust the timestamp by adding 3 hours if data is available
    adjusted_timestamp = None
    if temperature_data:
        adjusted_timestamp = temperature_data.timestamp + timedelta(hours=3)

    context = {
        'temperature_data': temperature_data,
        'adjusted_timestamp': adjusted_timestamp,
        'max_temperature': max_temperature,
        'min_temperature': min_temperature,
        'avg_temperature': avg_temperature,
    }

    return render(request, 'sensor/user_temperature_data.html', context)



#I did not understand this function
def offer_service(request):
    if request.method == 'POST':
        # Retrieve form data
        service_type = request.POST.get('service_type')
        service_description = request.POST.get('service_description')
        price = request.POST.get('price')
        
        # Save the service to the database
        offered_service = OfferedService(
            service_type=service_type,
            description=service_description,
            price=price,
        )
        offered_service.save()

        # Redirect to a confirmation page or render a response
        return HttpResponse("Service connected and offered successfully!, use the following IP address to publish the data 192.168.100.112")

    return render(request, 'services/offer.html')



def service_list(request):
    services = OfferedService.objects.all()  # Retrieve all services
    return render(request, 'sensor/service_list.html', {'services': services})
