import random
import time
import json
import paho.mqtt.client as mqtt
import requests
from threading import Thread

# MQTT settings
Broker = "test.mosquitto.org"          # Defining the MQTT Broker.
MQTT_BROKER = Broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

# REST API settings
REST_API_URL = "http://your_rest_api_endpoint"

# Error handling function
def simulate_error(chance=0.01):
    if random.random() < chance:
        raise Exception("Simulated sensor error")

# Temperature Sensor
def temperature_sensor():
    while True:
        try:
            simulate_error()
            temperature = random.gauss(22, 2)  # Normal distribution around 22°C
            data = {"sensor": "temperature", 
                    "value": temperature, 
                    "unit": "°C", 
                    "timestamp": time.time()}
            publish_data(data)
        except Exception as e:
            print(f"Temperature sensor error: {e}")
        time.sleep(1)                 # Generating a reading every 1 sec.

# Air Pollution Sensor
def air_pollution_sensor():
    while True:
        try:
            simulate_error()
            air_quality = random.gauss(50, 15)  # Normal distribution around 50 AQI
            data = {"sensor": "air_pollution", "value": air_quality, "unit": "AQI", "timestamp": time.time()}
            publish_data(data)
        except Exception as e:
            print(f"Air Pollution sensor error: {e}")
        time.sleep(1)                 # Generating a reading every 1 sec.

# Heart Rate Monitor
def heart_rate_monitor():
    while True:
        try:
            simulate_error()
            heart_rate = random.gauss(70, 10)  # Normal distribution around 70 BPM
            data = {"sensor": "heart_rate", "value": heart_rate, "unit": "BPM", "timestamp": time.time()}
            publish_data(data)
        except Exception as e:
            print(f"Heart Rate Monitor error: {e}")
        time.sleep(60)                 # Generating a reading every 60 sec.

# Blood Oxygen Level Monitor
def blood_oxygen_level_monitor():
    while True:
        try:
            simulate_error()
            blood_oxygen_level = random.gauss(98, 1)  # Normal distribution around 98%
            data = {"sensor": "blood_oxygen_level", "value": blood_oxygen_level, "unit": "%", "timestamp": time.time()}
            publish_data(data)
        except Exception as e:
            print(f"Blood Oxygen Level Monitor error: {e}")
        time.sleep(60)                 # Generating a reading every 60 sec.

# Function to publish data via MQTT and REST
def publish_data(data):
    json_data = json.dumps(data)
    print(json_data)
    # Publish to MQTT
    mqtt_client.publish(MQTT_TOPIC, json_data)
    # Send to REST API
    # requests.post(REST_API_URL, json=json_data)        ## Uncomment this line for Posting with REST. 

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start sensor threads
sensors = [temperature_sensor, air_pollution_sensor, heart_rate_monitor, blood_oxygen_level_monitor]

threads = []
for sensor in sensors:
    thread = Thread(target=sensor)
    thread.start()
    threads.append(thread)

# Keep main thread alive
for thread in threads:
    thread.join()
