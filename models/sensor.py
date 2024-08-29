from typing import Literal
from models.publisher import sensorPublisher

TipoSensor = Literal["Temperatura", "Humidade", "Velocidade"]

class Sensor:
  def __init__(
      self,
      tipo: TipoSensor,
      nome: str,
      min: float,
      max: float,
    ) -> None:
    self.tipo = tipo
    self.nome = nome
    self.min = min
    self.max = max
    self.topico = f"topic/{tipo}-{nome}"

    self.valor = (min+max)/2
  
  def setValor(self, valor: float):
    self.valor = valor
    self._notifica(f"{self.valor}")
    if valor <= self.min:
      self._notificaCritico(f"{self.valor} (- {self.min - valor})")
    if valor >= self.max:
      self._notificaCritico(f"{self.valor} (+ {valor - self.max})")

  def _notifica(self, msg: str):
    sensorPublisher.publish(self.topico, msg)

  def _notificaCritico(self, msg: str):
    sensorPublisher.publish(f"critic{self.topico}", msg)
