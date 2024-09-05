import paho.mqtt.client as mqtt

broker = "localhost"
port = 1883

servidorPublisher = mqtt.Client()
servidorPublisher.connect(broker, port)
