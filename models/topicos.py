from models.publisher import sensorPublisher

class _TopicosMOM:
  def __init__(self):
    self.topicos: list[str] = []
    self.clientes: list[str] = []
    self.mudanca_topico = "topic/topics_change"

  def adicionarTopico(self, topico: str) -> bool:
    novoTopico = f"topic/{topico}"
    if self.topicos.count(novoTopico) > 0:
      return False

    self.topicos.append(novoTopico)
    sensorPublisher.publish(self.mudanca_topico, f"add:{novoTopico}")
    return True

  def removerTopico(self, topico: str) -> bool:
    topicoRemover = f"topic/{topico}"
    try:
      index = self.topicos.index(topicoRemover)
      self.topicos.remove(topicoRemover)
      sensorPublisher.publish(self.mudanca_topico, f"remove:{index}")

      return True
    except Exception as e:
      print(f"ERRO removerTopico: {e}")
      return False

  def adicionarCliente(self, cliente: str) -> bool:
    novoCliente = cliente
    if self.clientes.count(novoCliente) > 0:
      return False

    self.clientes.append(novoCliente)
    return True

  def removerCliente(self, cliente: str) -> bool:
    try:
      self.clientes.remove(cliente)
      return True
    except Exception as e:
      return False

topicosMOM = _TopicosMOM()