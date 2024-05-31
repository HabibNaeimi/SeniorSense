import random
import time
import json
import paho.mqtt.client as mqtt
import requests

"""
This script simulates a Blood Oxygen Level Monitor that generates blood oxygen level readings (percentage) 
every minute. The generated data is published to an MQTT broker and sent to a REST API endpoint. 
The script also includes error handling to simulate occasional sensor malfunctions.
"""

# MQTT settings
Broker = "test.mosquitto.org"          # Defining the MQTT Broker.
MQTT_BROKER = Broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/blood_oxygen_level"

# REST API settings
REST_API_URL = "http://your_rest_api_endpoint"

def simulate_error(chance=0.01):
    if random.random() < chance:
        raise Exception("Simulated sensor error")

def blood_oxygen_level_monitor():
    while True:
        try:
            simulate_error()
            blood_oxygen_level = random.gauss(98, 1)  # Normal distribution around 98%
            data = {"sensor": "blood_oxygen_level", "value": blood_oxygen_level, "unit": "%", "timestamp": time.time()}
            publish_data(data)
        except Exception as e:
            print(f"Blood Oxygen Level Monitor error: {e}")
        time.sleep(60)

def publish_data(data):
    json_data = json.dumps(data)
    print(json_data)
    # Publish to MQTT
    mqtt_client.publish(MQTT_TOPIC, json_data)
    # Send to REST API
    # requests.post(REST_API_URL, json=json_data)     ## Uncomment this line for Posting with REST.

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the sensor
blood_oxygen_level_monitor()
