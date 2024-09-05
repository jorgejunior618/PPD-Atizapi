import Pyro4
from abc import ABC, abstractmethod

class IServidorOffline(ABC):
  _mensagens = dict[str, dict[str, list[str]]]
  _usuarios = dict[str, bool]

  @property
  @abstractmethod
  def mensagens(self) -> dict[str, dict[str, list[str]]]:
    pass
  @mensagens.setter
  @abstractmethod
  def mensagens(self, nv: list[str]):
    pass

  @property
  @abstractmethod
  def usuarios(self) -> dict[str, bool]:
    pass
  @usuarios.setter
  @abstractmethod
  def usuarios(self, nv: dict[str, bool]):
    pass
  @abstractmethod
  def adicionarUsuario(self, nuser: str) -> bool:
    pass

  @abstractmethod
  def enviarMensagem(self, remetente: str, destino: str, mensagem: str):
    pass

  @abstractmethod
  def checarMensagens(self, cliente: str) -> dict[str, int]:
    pass

  @abstractmethod
  def receberMensagens(self, cliente: str, enviadoPor: str) -> list[str]:
    pass

  @abstractmethod
  def adicionarAmigo(self, cliente: str, amigo: str):
    pass

  @abstractmethod
  def desfazerAmizade(self, cliente: str, amigo: str):
    pass

  @abstractmethod
  def mudarStatus(self, cliente: str, status: bool):
    pass

uri = "PYRONAME:mensageiro.servidor"
servidorMensagens: IServidorOffline = Pyro4.Proxy(uri)
