import random
import time
import json
import paho.mqtt.client as mqtt
import requests

"""
This script simulates a Temperature Sensor that generates temperature readings in °C every second. 
The generated data is published to an MQTT broker and sent to a REST API endpoint. The script also 
includes error handling to simulate occasional sensor malfunctions.
"""


# MQTT settings
Broker = "test.mosquitto.org"          # Defining the MQTT Broker.
MQTT_BROKER = Broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

# REST API settings
REST_API_URL = "http://your_rest_api_endpoint"

def simulate_error(chance=0.01):
    if random.random() < chance:
        raise Exception("Simulated sensor error")

def temperature_sensor():
    while True:
        try:
            simulate_error()
            temperature = random.gauss(22, 2)  # Normal distribution around 22°C
            data = {"sensor": "temperature", "value": temperature, "unit": "°C", "timestamp": time.time()}
            publish_data(data)
        except Exception as e:
            print(f"Temperature sensor error: {e}")
        time.sleep(1)

def publish_data(data):
    json_data = json.dumps(data)
    print(json_data)
    # Publish to MQTT
    mqtt_client.publish(MQTT_TOPIC, json_data)
    # Send to REST API
    # requests.post(REST_API_URL, json=json_data)   ## Uncomment this line for Posting with REST.

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the sensor
temperature_sensor()
