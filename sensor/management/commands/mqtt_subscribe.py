import paho.mqtt.client as mqtt
from sensor.models import Subscription, TemperatureData, OfferedService
from datetime import datetime, timedelta
import json
from django.utils import timezone

# MQTT Configuration
broker = "192.168.100.112"
port = 1883

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    
    # Subscribe to all service topics using a wildcard
    client.subscribe("sensor/+/data")

def on_message(client, userdata, msg):
    try:
        # Decode and parse the JSON payload
        data = json.loads(msg.payload.decode())
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        # Ensure valid data
        if temperature is None or humidity is None:
            print("Invalid data received, discarding...")
            return

        # Extract the service ID from the topic (assuming 'sensor/<service_id>/data')
        topic_parts = msg.topic.split("/")
        service_id = int(topic_parts[1])  # Extract the service ID from the topic

        # Get the service
        service = OfferedService.objects.filter(id=service_id).first()
        if not service:
            print(f"Service ID {service_id} not found, discarding data.")
            return

        # Get subscriptions linked to the service
        subscriptions = Subscription.objects.filter(service=service)
        if not subscriptions.exists():
            print(f"No subscribers for Service ID {service_id}, discarding data.")
            return

        # Process data for each subscription
        for subscription in subscriptions:
            # Check subscription criteria
            readings_count = TemperatureData.objects.filter(subscription=subscription).count()
            if readings_count >= subscription.subscription_duration:
                print(f"Subscription ID {subscription.id}: Max readings reached, skipping.")
                continue

            last_reading = TemperatureData.objects.filter(subscription=subscription).order_by('-timestamp').first()
            if last_reading:
                # Make sure last_reading.timestamp is timezone-aware
                last_timestamp = timezone.make_aware(last_reading.timestamp) if timezone.is_naive(last_reading.timestamp) else last_reading.timestamp
                time_difference = timezone.now() - last_timestamp
                required_interval = timedelta(hours=subscription.interval_between_readings)

                if time_difference < required_interval:
                    print(f"Subscription ID {subscription.id}: Interval not met, skipping.")
                    continue

            # Save data
            TemperatureData.objects.create(
                subscription=subscription,
                temperature=temperature,
                humidity=humidity,
                timestamp=timezone.now()  # Use timezone-aware datetime
            )
            print(f"Data saved for subscription ID {subscription.id}")
    except json.JSONDecodeError:
        print("Error decoding JSON message.")
    except Exception as e:
        print(f"Error processing message: {e}")
  

# Create MQTT client and set callbacks
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker and start the loop
try:
    client.connect(broker, port, 60)
    print("MQTT client connected successfully.")
    client.loop_forever()
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
