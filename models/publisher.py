import paho.mqtt.client as mqtt

broker = "localhost"
port = 1883

sensorPublisher = mqtt.Client()
sensorPublisher.connect(broker, port)
