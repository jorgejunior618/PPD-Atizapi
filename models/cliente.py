import paho.mqtt.client as mqtt
from typing import Callable, Any

CallbackOnMessage = Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None]

class Cliente:
  def __init__(self, nome: str) -> None:
    self.nome = nome

    self.client = mqtt.Client()
    self.client.connect("localhost", 1883)

  def inicializaCliente(self, onMessage: CallbackOnMessage) -> None:
    self.client.on_message = onMessage

    self.client.loop_forever()

  def adicionarAmigo(self, novoAmigo: str):
    topico = f"{self.nome}/{novoAmigo}"
    self.client.subscribe(topico)

  def desfazerAmizade(self, novoAmigo: str):
    self.client.unsubscribe(f"{self.nome}/{novoAmigo}")
