import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from sensor.models import TemperatureData
from django.contrib.auth.models import User
import json

class Command(BaseCommand):
    help = 'Subscribe to MQTT broker and store sensor data'

    def handle(self, *args, **kwargs):
        def on_connect(client, userdata, flags, rc):
            print(f"Connected with result code {rc}")
            # Subscribe to the topic where both temperature and humidity are published
            client.subscribe("sensor/+/data")

        def on_message(client, userdata, msg):
            try:
                # Decode the message payload
                message = msg.payload.decode()
                data = json.loads(message)  # Parse JSON payload

                topic_parts = msg.topic.split("/")
                user_id = topic_parts[1]  # Assuming the topic structure is 'sensor/<user_id>/data'

                # Extract data from JSON payload
                temperature = data.get("temperature")
                humidity = data.get("humidity")

                # Ensure both temperature and humidity exist
                if temperature is not None and humidity is not None:
                    # Get the user associated with the topic
                    user = User.objects.get(id=user_id)
                    
                    # Save data to the database
                    TemperatureData.objects.create(
                        user=user,
                        temperature=temperature,
                        humidity=humidity
                    )
                    print(f"Data saved for user {user.username}: Temp={temperature}°C, Humidity={humidity}%")
                else:
                    print("Invalid data format received:", data)

            except json.JSONDecodeError:
                print("Failed to decode JSON message:", msg.payload.decode())
            except User.DoesNotExist:
                print(f"User with ID {user_id} not found")
            except Exception as e:
                print(f"Error processing message: {e}")

        # Create MQTT client and set callbacks
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        # Connect to the MQTT broker
        client.connect("192.168.100.112", 1883, 60)  # Use your server's IP
        client.loop_forever()
