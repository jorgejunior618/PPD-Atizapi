import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import paho.mqtt.client as mqtt
from threading import Thread

from tkinter import Toplevel, Tk, StringVar, BooleanVar, Listbox, Scrollbar, Entry, Checkbutton
from tkinter.font import Font
from tkinter.ttk import Style, Label, Button
from typing import Literal, Any, Callable

from models.cliente import Cliente
from models.i_serv_mensagens import servidorMensagens
from pygame import mixer
import time

CallbackOnMessage = Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None]
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
