# i_serv_mensagens.py

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

# cliente.py

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

#publisher.py

broker = "localhost"
port = 1883

servidorPublisher = mqtt.Client()
servidorPublisher.connect(broker, port)

#servidor_mensagens.py

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

#gui_principal.py

from tkinter import Tk, StringVar
from tkinter.font import Font
from tkinter.ttk import Style, Button, Label, Entry


TELA_NORMAL = "270x115"


class GuiObjectBuilder:
  def __init__(self):
    self.criandoSensor = False
    self.criandoCliente = False

    self.criaComponenteJanela()
    self.isntanciarEstilos()
    self.criaComponentesNovoUsuario()

  def criaComponenteJanela(self):
    self.janela = Tk()
    self.janela.title("Atizapi ☏")
    self.janela.geometry(TELA_NORMAL)
    self.janela.resizable(False, False)

  def isntanciarEstilos(self):
    self.fonteGeral = Font(size=12, family="Trebuchet MS")
    self.fonteLeitura = Font(size=9, family="Trebuchet MS")

    style = Style()
    style.configure("Gen.Label", font=self.fonteGeral)
    style.configure("Err.Label", font=self.fonteLeitura, foreground="#F02424")
    style.configure("Info.Label", font=self.fonteLeitura, foreground="#A0A0A0")
    style.configure("Ger.TButton", width=12, font=self.fonteGeral)

  def criaComponentesNovoUsuario(self):
    self.varNome = StringVar()

    self.lblNmUsuario = Label(self.janela, text="Nome do novo usuario", style="Gen.Label")
    self.lblInfoBotao = Label(self.janela, text= "Clique para\nmais um usuário", style="Info.Label")
    self.lblErroNome = Label(self.janela, text= "", style="Err.Label")
    self.inputNmUsuario = Entry(self.janela, textvariable=self.varNome, width=16, font=self.fonteGeral)
    self.botNovoSensor = Button(self.janela, text="Novo usuário", command=self.instanciarNovoUsuario, style="Ger.TButton")
  
    self.lblNmUsuario.place(x=30, y=5)
    self.lblInfoBotao.place(x=140, y=67)
    self.lblErroNome.place(x=30, y=52)
    self.inputNmUsuario.place(x=30, y=25)
    self.botNovoSensor.place(x=30, y=70)
    self.inputNmUsuario.focus()
    def bindEnter(kc):
      if kc == 13: # Pressionou enter
        self.instanciarNovoUsuario()
    self.inputNmUsuario.bind("<Key>", lambda e: bindEnter(e.keycode))

  def instanciarNovoUsuario(self):
    if self.validaNome():
      try:
        clienteNovo = Cliente(self.varNome.get())
        usuarioGui = GuiCliente(clienteNovo, self.janela)
        self.preparaNovoInput()
        usuarioGui.iniciaAplicacao()
      except Exception as e:
        return False

  def preparaNovoInput(self):
    try:
      self.lblErroNome.configure(text="")
      self.varNome.set("")
    except Exception as e:
      print("erro removeComponentesNovoSensor: ", e)
  
  def validaNome(self):
    nome = self.varNome.get()
    if len(nome) < 3:
      self.lblErroNome.configure(text="Use mais de 3 caracteres")
      return False
    if not nome.isalnum():
      self.lblErroNome.configure(text="Não use pontuações")
      return False
    if not servidorMensagens.adicionarUsuario(nome):
      self.lblErroNome.configure(text="Nome já cadastrado")
      return False
    return True

  def iniciaAplicacao(self):
    self.janela.mainloop()

# gui_cliente.py

from threading import Thread

from tkinter import Toplevel, Tk, StringVar, BooleanVar, Listbox, Scrollbar, Entry, Checkbutton
from tkinter.font import Font
from tkinter.ttk import Style, Label, Button
from typing import Literal

from pygame import mixer
import time

TipoSensor = Literal["Temperatura", "Humidade", "Velocidade"]

TELA_ATIVO = "500x300"
TELA_ADD_AMIGO = "700x300"

class GuiCliente:
  def __init__(self, cliente: Cliente, raiz: Tk):
    self.raiz = raiz
    self.cliente = cliente
    self.amizades = []
    self.online = True
    mixer.init()

  def inicializaCliente(self):
    thread_client = Thread(target=self.cliente.inicializaCliente, args=[self.onMessageClient()], daemon=True)
    thread_client.start()

  def onselectConversa(self):
    try:
      selecionados: list[int] = list(self.lbxAmigos.curselection())
      if len(selecionados) == 0: pass
      elif len(selecionados) == 1: self.conversaAtual = selecionados[0]
      else:
        selecionados.remove(self.conversaAtual)

        self.lbxAmigos.selection_clear(self.conversaAtual, self.conversaAtual)
        self.lbxAmigos.selection_set(selecionados[0], selecionados[0])
        self.conversaAtual = selecionados[0]
      if len(selecionados) > 0:
        self.mensagens = servidorMensagens.receberMensagens(self.cliente.nome, self.amizades[selecionados[0]])
        self.varMensagens.set(value=self.mensagens)
        self.inputNovaMsg.focus_set()
    except Exception as e:
      print(f"ERRO onselect: {self.cliente.nome ,e}")
      return False

  def finalizarAddAmigo(self):
      self.lbxNovosAmigos.destroy()
      self.janela.geometry(TELA_ATIVO)
      self.btnNovoAmigo.configure(text="Adicionar Amigo", command=lambda: self.criaComponentesAddAmigo())

  def onselectNovoAmigo(self):
    try:
      selecionado: int = list(self.lbxNovosAmigos.curselection())[0]
      usuarios = [usr for usr in servidorMensagens.usuarios]
      amizade = usuarios[selecionado]
      if amizade == self.cliente.nome or amizade in self.amizades:
        self.lbxNovosAmigos.select_clear(selecionado)
        return
      self.amizades.append(amizade)
      self.varAmizades.set(value=self.amizades)
      self.cliente.adicionarAmigo(amizade)
      servidorMensagens.adicionarAmigo(self.cliente.nome, amizade)
      self.finalizarAddAmigo()
    except Exception as e:
      print(f"ERRO onselectNovo amigo: {e}")
      return False

  def notificacao(self, naConversa=False):
    mixer.music.load("assets/mensagem-conversa.mp3" if naConversa else "assets/notificacao.mp3")
    mixer.music.set_volume(0.7)
    mixer.music.play()

  def onMessageClient(self) -> CallbackOnMessage:
    def onMessageFunc(cli: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
      msg = message.payload.decode()
      topico = message.topic
      remetente = topico.split("/")[1]

      if self.conversaAtual >= 0 and remetente == self.amizades[self.conversaAtual]:
        self.notificacao(naConversa=True)
        self.mensagens = servidorMensagens.receberMensagens(self.cliente.nome, remetente)
        self.varMensagens.set(value=self.mensagens)
      else:
        # index = self.amizades.index(remetente)
        lblIndNvMsg = Label(self.janela, text=f"Mensagem de {remetente}", style="Plc.Label")
        lblIndNvMsg.place(x=300, y=150)
        self.notificacao()
        def removerAlerta():
          time.sleep(2)
          lblIndNvMsg.destroy()
        threadLimparAlerta = Thread(target=removerAlerta, daemon=True)
        threadLimparAlerta.start()
    return onMessageFunc

  def criaComponenteJanela(self):
    self.janela = Toplevel(self.raiz)
    self.janela.title("Atizapi - Chat Online")
    self.janela.geometry(TELA_ATIVO)
    self.janela.resizable(False, False)

  def criaComponenteEstilos(self):
    self.fonteGeral = Font(size=12, family="Trebuchet MS")
    self.fonteLeitura = Font(size=9, family="Trebuchet MS")

    style = Style()
    style.configure("Gen.Label", font=self.fonteGeral)
    style.configure("Peq.Label", font=self.fonteLeitura)
    style.configure("Plc.Label", font=self.fonteLeitura, foreground="#A0A0A0")
    style.configure("Err.Label", font=self.fonteLeitura, foreground="#F02424")
    style.configure("Enviar.TButton", width=8, font=self.fonteGeral)
    style.configure("Add.TButton", width=15, font=self.fonteGeral)

  def enviarMensagem(self):
    if self.conversaAtual == -1: return
    destino = self.amizades[self.conversaAtual]
    msg = self.varNovaMsg.get()
    servidorMensagens.enviarMensagem(self.cliente.nome, destino, msg)
    self.varNovaMsg.set("")
    self.mensagens = servidorMensagens.receberMensagens(self.cliente.nome, destino)

    self.varMensagens.set(value=self.mensagens)

  def criaInicializadorCliente(self):
    self.varAmizades = StringVar(value=[])
    self.varMensagens = StringVar(value=[])
    self.varOnline = BooleanVar(value=True)
    self.varNomeSensor = StringVar()
    self.varNovaMsg = StringVar()
    self.varLeituras: list[StringVar] = []

    self.mensagens = []

    self.conversaAtual = -1

    yscrollbar = Scrollbar(self.janela)

    def toggleCheckbox():
      self.online = self.varOnline.get()
      servidorMensagens.mudarStatus(self.cliente.nome, self.online)
      if self.online and self.conversaAtual != -1:
        msgAtual = servidorMensagens.receberMensagens(self.cliente.nome, self.amizades[self.conversaAtual])
        if len(msgAtual) > len(self.mensagens):
          self.notificacao(naConversa=True)
          self.mensagens = msgAtual[:]
          self.varMensagens.set(value=self.mensagens)

  
    self.listLblAssinados: list[Label | None] = []
    self.lblNomeCliente = Label(self.janela, text=f"Cliente: {self.cliente.nome}", style="Gen.Label")
    self.chkbtnOnline = Checkbutton(
      self.janela,
      text="Online",
      variable=self.varOnline,
      onvalue=True,
      offvalue=False,
      command=toggleCheckbox
    )
    self.inputNovaMsg = Entry(self.janela, textvariable=self.varNovaMsg, width=16, font=self.fonteGeral)
    self.btnNovaMsg = Button(self.janela, text="Enviar", command=lambda : self.enviarMensagem(), style="Enviar.TButton")
    self.btnNovoAmigo = Button(self.janela, text="Adicionar Amigo", command=lambda: self.criaComponentesAddAmigo(), style="Add.TButton")
    self.lblIndcadorAmigos = Label(self.janela, text="Seus amigos", style="Gen.Label")
    self.lblIndicadorConversa = Label(self.janela, text="Conversa", style="Gen.Label")
    self.lblNovaMsg = Label(self.janela, text="Nova mensagem", style="Plc.Label")

    self.lbxAmigos = Listbox(
      self.janela,
      selectmode="multiple",
      width=34,
      height=11,
      font=self.fonteLeitura,
      yscrollcommand=yscrollbar.set,
      listvariable=self.varAmizades, 
    )
    self.lbxConversa = Listbox(
      self.janela,
      selectmode="multiple",
      width=34,
      height=9,
      font=self.fonteLeitura,
      listvariable=self.varMensagens,
    )

    self.lblNomeCliente.place(x=30, y=10)
    self.chkbtnOnline.place(x=250, y=10)
    self.lblIndcadorAmigos.place(x=30, y=50)
    self.lblIndicadorConversa.place(x=260, y=50)

    self.lbxAmigos.place(x=30, y=70)
    self.lbxConversa.place(x=260, y=70)
    self.inputNovaMsg.place(x=260, y=250)
    self.btnNovaMsg.place(x=400, y=248)
    self.lblNovaMsg.place(x=260, y=275)

    self.btnNovoAmigo.place(x=340, y=7)

    yscrollbar.place(x=236, y=70, height=3+ 10 * 19, width=17)
    yscrollbar.configure(command=self.lbxAmigos.yview)

    self.lbxAmigos.bind('<<ListboxSelect>>', lambda _: self.onselectConversa())
    def bindEnter(kc):
      if kc == 13: # Pressionou enter
        self.enviarMensagem()
    self.inputNovaMsg.bind("<Key>", lambda e: bindEnter(e.keycode))

  def criaComponentesAddAmigo(self):
    self.btnNovoAmigo.configure(text="Cancelar", command=lambda: self.finalizarAddAmigo())

    self.janela.geometry(TELA_ADD_AMIGO)
    varNovasAmizades = StringVar(value=[usr if usr != self.cliente.nome else f"{usr} - Você" for usr in servidorMensagens.usuarios])

    self.btnNovaMsg
    self.lbxNovosAmigos = Listbox(
      self.janela,
      selectmode="multiple",
      width=34,
      height=9,
      font=self.fonteLeitura,
      listvariable=varNovasAmizades, 
    )
    self.lbxNovosAmigos.place(x=480, y=70)
    self.lbxNovosAmigos.bind('<<ListboxSelect>>', lambda _: self.onselectNovoAmigo())


  def iniciaAplicacao(self):
    self.criaComponenteJanela()
    self.inicializaCliente()
    self.criaComponenteEstilos()
    self.criaInicializadorCliente()

# index.py

mainGui = GuiObjectBuilder()
mainGui.iniciaAplicacao()
