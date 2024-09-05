import Pyro4
from models.publisher import servidorPublisher
from models.i_serv_mensagens import IServidorOffline

class ServidorMensagens(IServidorOffline):
  def __init__(self):
    self._mensagens: dict[str, dict[str, list[str]]] = {}
    self._usuarios: dict[str, bool] = {}

  @property
  @Pyro4.expose
  def mensagens(self) -> dict[str, dict[str, list[str]]]:
    return self._mensagens

  @mensagens.setter
  @Pyro4.expose
  def mensagens(self, nv: dict[str, dict[str, list[str]]]):
    self._mensagens = nv

  @property
  @Pyro4.expose
  def usuarios(self) -> dict[str, bool]:
    return self._usuarios

  @usuarios.setter
  @Pyro4.expose
  def usuarios(self, nv: dict[str, bool]):
    self._usuarios = nv

  @Pyro4.expose
  def adicionarUsuario(self, nuser: str) -> bool:
    if self._usuarios.get(nuser) != None: return False 
    self._usuarios[nuser] = True 
    self._mensagens[nuser] = {}
    return True

  @Pyro4.expose
  def enviarMensagem(self, remetente: str, destino: str, mensagem: str):
    if self._mensagens[remetente][destino] == None: 
      self._mensagens[remetente][destino] = [f"você: {mensagem}"]
    else:
      self._mensagens[remetente][destino].append(f"você: {mensagem}")
    if self._mensagens[destino][remetente] == None: 
      self._mensagens[destino][remetente] = [f"{remetente}: {mensagem}"]
    else:
      self._mensagens[destino][remetente].append(f"{remetente}: {mensagem}")
    if self._usuarios[destino]:
      servidorPublisher.publish(f'{destino}/{remetente}', mensagem)

  @Pyro4.expose
  def checarMensagens(self, cliente: str) -> dict[str, int]:
    listaMensagens: dict[str, int] = {}
    for amigo in self._mensagens[cliente]:
      listaMensagens[amigo] = len(self._mensagens[cliente][amigo])
    return listaMensagens

  @Pyro4.expose
  def receberMensagens(self, cliente: str, amigo: str) -> list[str]:
    msgs = self._mensagens[cliente][amigo][:]
    return msgs

  @Pyro4.expose
  def adicionarAmigo(self, cliente: str, amigo: str):
    if self._mensagens[cliente].get(amigo) == None: 
      self._mensagens[cliente][amigo] = []
      self._mensagens[amigo][cliente] = []

  @Pyro4.expose
  def desfazerAmizade(self, cliente: str, amigo: str):
    self._mensagens[cliente][amigo] = None

  @Pyro4.expose
  def mudarStatus(self, cliente: str, status: bool):
    self._usuarios[cliente] = status
