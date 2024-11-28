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
from django.http import JsonResponse
from django.http import HttpResponseForbidden
import pandas as pd
from math import radians, cos, sin, sqrt, atan2


def download_data(request):
   

    # Fetch data for subscriptions of the logged-in user
    subscriptions = Subscription.objects.filter(user=request.user)
    temperature_data = TemperatureData.objects.filter(subscription__in=subscriptions).order_by('timestamp')

    # Prepare data for the Excel file
    data = [
        {
            'Date': (record.timestamp + timedelta(hours=3)).date(),
            'Time': (record.timestamp + timedelta(hours=3)).time(),
            'Temperature (°C)': record.temperature,
            'Humidity (%)': record.humidity,
        }
        for record in temperature_data
    ]

    # Convert data to a DataFrame
    df = pd.DataFrame(data)

    # Create the Excel file in memory
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=temperature_data.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Temperature Data')

    return response


@login_required
def my_subscriptions(request):
    # Filter subscriptions by the logged-in user
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'sensor/my_subscriptions.html', {'subscriptions': subscriptions})





# def send_mqtt_notification(user_id, interval, duration, topic):
#     """Sends an MQTT message to notify about a new subscription."""
#     mqtt_broker = "192.168.100.112"  # Update with your MQTT broker IP
#     mqtt_port = 1883
#     client = mqtt.Client()
    
#     # Attempt connection with logging
#     try:
#         print("Attempting to connect to MQTT broker...")
#         client.connect(mqtt_broker, mqtt_port, 60)
#         print("Connected to MQTT broker.")
        
#         # Construct the message
#         message = f"You have a new subscriber with user ID {user_id}. Publish the data every {interval} for {duration} to this topic {topic}."
#         print(f"Publishing message: {message}")
        
#         # Publish the message
#         client.publish("sensor/subscriptions", message)
#         print("Message published successfully.")
        
#     except Exception as e:
#         print(f"Failed to send MQTT message: {e}")
#     finally:
#         # Disconnect after publishing
#         client.disconnect()
#         print("Disconnected from MQTT broker.")
        
@login_required
def subscribe(request, service_id):
    if request.method == 'POST':
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

        # user_topic = f"sensor/{user.id}/data"
        
        # Send MQTT notification
        # send_mqtt_notification(
        #     user_id=user.id,
        #     interval=interval_between_readings,
        #     duration=subscription_duration,
        #     topic=user_topic
        # )

        # Add a success message for user feedback
        # messages.success(request, "You have successfully subscribed to the service.")
        
        return redirect('sensor:my_subscriptions') #--> this line is the error 

    print("Redirecting back to service list without subscribing.")
    return redirect('sensor:service_list')


# def send_mqtt_edit_notification(topic, message):
#     """Sends an MQTT message to notify about a subscription update."""
#     mqtt_broker = "192.168.100.112"  # Update with your MQTT broker IP
#     mqtt_port = 1883
#     client = mqtt.Client()
    
#     try:
#         print("Attempting to connect to MQTT broker...")
#         client.connect(mqtt_broker, mqtt_port, 60)
#         print("Connected to MQTT broker.")
        
#         # Log the topic and message
#         print(f"Publishing to topic: {topic}")
#         print(f"Message: {message}")
        
#         # Publish the message
#         client.publish(topic, message)
#         print("Message published successfully.")
#     except Exception as e:
#         print(f"Failed to send MQTT message: {e}")
#     finally:
#         # Disconnect after publishing
#         client.disconnect()
#         print("Disconnected from MQTT broker.")

def edit_subscription(request, subscription_id):
    """Allows the user to edit an existing subscription and notifies the service provider."""
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)

    if request.method == 'POST':
        # Get the old values for comparison
        old_duration = subscription.subscription_duration
        old_interval = subscription.interval_between_readings

        # Update subscription details from form data
        subscription.subscription_duration = request.POST.get('subscription_duration')
        subscription.interval_between_readings = request.POST.get('interval_between_readings')
        subscription.save()

        # If the subscription details have changed, notify the service provider
        if old_duration != subscription.subscription_duration or old_interval != subscription.interval_between_readings:
            service_provider_topic = "sensor/subscriptions"
            message = (
                f"User {request.user.id} has updated their subscription:\n"
                f"- Service: {subscription.service.service_type}\n"
                f"- New Duration: {subscription.subscription_duration}\n"
                f"- New Interval: {subscription.interval_between_readings}\n"
                f"- please Publish the data to: sensor/{request.user.id}/data"
            )
            # Send the MQTT message to the service provider
            # send_mqtt_edit_notification(topic=service_provider_topic, message=message)

        return redirect('sensor:my_subscriptions')

    # Render the edit form with current subscription details
    return render(request, 'sensor/edit_subscription.html', {'subscription': subscription})


def delete_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    subscription.delete()
    return redirect('sensor:my_subscriptions')



@login_required
def user_temperature_data(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)

    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter data for this subscription
    temperature_data = TemperatureData.objects.filter(subscription=subscription).order_by('timestamp')

    if start_date:
        temperature_data = temperature_data.filter(timestamp__date__gte=start_date)
    if end_date:
        temperature_data = temperature_data.filter(timestamp__date__lte=end_date)

    # Calculate statistics
    max_temperature = temperature_data.aggregate(Max('temperature'))['temperature__max']
    min_temperature = temperature_data.aggregate(Min('temperature'))['temperature__min']
    avg_temperature = temperature_data.aggregate(Avg('temperature'))['temperature__avg']
    max_humidity = temperature_data.aggregate(Max('humidity'))['humidity__max']
    min_humidity = temperature_data.aggregate(Min('humidity'))['humidity__min']
    avg_humidity = temperature_data.aggregate(Avg('humidity'))['humidity__avg']

    # Adjust data for table
    adjusted_data = [
        {
            'date': (entry.timestamp + timedelta(hours=3)).date(),
            'time': (entry.timestamp + timedelta(hours=3)).time(),
            'temperature': entry.temperature,
            'humidity': entry.humidity,
        }
        for entry in temperature_data
    ]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'data': adjusted_data})

    context = {
        'subscription': subscription,
        'adjusted_data': adjusted_data,
        'max_temperature': max_temperature,
        'min_temperature': min_temperature,
        'avg_temperature': avg_temperature,
        'max_humidity': max_humidity,
        'min_humidity': min_humidity,
        'avg_humidity': avg_humidity,
    }
    return render(request, 'sensor/user_temperature_data.html', context)



def offer_service(request):
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        service_description = request.POST.get('service_description')
        price = request.POST.get('price')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Save the service with location data
        new_service = OfferedService.objects.create(
            service_type=service_type,
            description=service_description,
            price=price,
            latitude=latitude,
            longitude=longitude
        )

        # Render a confirmation page with the details
        context = {
            'service_type': service_type,
            'service_description': service_description,
            'price': price,
            'latitude': latitude,
            'longitude': longitude,
            'publish_topic': f"sensor/{new_service.id}/data"  # Include the service ID
        }
        return render(request, 'services/offer_success.html', context)

    return render(request, 'services/offer.html')




def haversine(lat1, lon1, lat2, lon2):
    # Convert database Decimal values to float
    lat2 = float(lat2)
    lon2 = float(lon2)
    
    # Calculate the great-circle distance between two points on the Earth
    R = 6371  # Radius of the Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def service_list(request):
    services = OfferedService.objects.all()
    latitude = request.GET.get("latitude")
    longitude = request.GET.get("longitude")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    radius = 10  # Default radius in km

    if latitude and longitude:
        latitude = float(latitude)
        longitude = float(longitude)

        # Filter by location
        filtered_services = []
        for service in services:
            distance = haversine(latitude, longitude, service.latitude, service.longitude)
            if distance <= radius:
                filtered_services.append(service)
        services = filtered_services

    # Filter by price range
    if min_price:
        services = [service for service in services if service.price >= float(min_price)]
    if max_price:
        services = [service for service in services if service.price <= float(max_price)]

    return render(request, 'sensor/service_list.html', {'services': services})