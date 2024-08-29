import paho.mqtt.client as mqtt
from typing import Callable, Any
from threading import Thread

CallbackOnMessage = Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None]

class Cliente:
  def __init__(self, nome: str) -> None:
    self.nome = nome

    self.client = mqtt.Client()
    self.client.connect("localhost", 1883)

  def inicializaCliente(self, onMessage: CallbackOnMessage) -> None:
    self.client.on_message = onMessage

    self.client.loop_forever()

  def inscreverTopico(self, topico: str):
    self.client.subscribe(topico)
    self.client.subscribe(f"critic{topico}")

  def desinscrever(self, topico: str):
    self.client.unsubscribe(topico)
    self.client.unsubscribe(f"critic{topico}")
