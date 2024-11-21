# management/commands/mqtt_subscribe.py
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from sensor.models import TemperatureData
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Subscribe to MQTT broker and store sensor data'

    def handle(self, *args, **kwargs):
       
        def on_connect(client, userdata, flags, rc):
            
            print(f"Connected with result code {rc}")
            client.subscribe("sensor/+/temperature")  # + allows us to capture the user ID in the topic

        def on_message(client, userdata, msg):
            message = msg.payload.decode()
            topic_parts = msg.topic.split("/")
            user_id = topic_parts[1]  # Assuming the topic structure is 'sensor/<user_id>/temperature'

            try:
                user = User.objects.get(id=user_id)
                # Save temperature data with the associated user
                TemperatureData.objects.create(user=user, data=message)
                print(f"Data saved for user {user.username}: {message}")
            except User.DoesNotExist:
                print(f"User with ID {user_id} not found")


      
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect("192.168.100.112", 1883, 60)  # Use your server's IP
        client.loop_forever()
