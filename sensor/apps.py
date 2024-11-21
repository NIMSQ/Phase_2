# # sensor/apps.py
# from django.apps import AppConfig
# from django.conf import settings
# import threading
# import paho.mqtt.client as mqtt

# class SensorConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'sensor'

#     def ready(self):
#         # Start the MQTT client when the Django server starts
#         if settings.RUNNING_SERVER:
#             mqtt_thread = threading.Thread(target=self.start_mqtt_client)
#             mqtt_thread.daemon = True  # Daemonize thread to stop it with Django
#             mqtt_thread.start()

#     def start_mqtt_client(self):
#         print("Starting MQTT client")

#         from .models import TemperatureData
#         from django.contrib.auth.models import User

#         def on_connect(client, userdata, flags, rc):
#             print(f"Connected with result code {rc}")
#             client.subscribe("sensor/+/temperature")

#         def on_message(client, userdata, msg):
#             message = msg.payload.decode()
#             topic_parts = msg.topic.split("/")
#             user_id = topic_parts[1]  # Extract user ID from topic

#             try:
#                 user = User.objects.get(id=user_id)
#                 TemperatureData.objects.create(user=user, data=message)
#                 print(f"Data saved for user {user.username}: {message}")
#             except User.DoesNotExist:
#                 print(f"User with ID {user_id} not found")

#         client = mqtt.Client()
#         client.on_connect = on_connect
#         client.on_message = on_message
#         client.connect("192.168.100.112", 1883, 60)
#         client.loop_forever()
