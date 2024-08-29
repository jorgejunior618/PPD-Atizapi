import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import paho.mqtt.client as mqtt
from threading import Thread

from tkinter import Toplevel, Tk, StringVar, Listbox, Scrollbar, Event
from tkinter.font import Font
from tkinter.ttk import Style, Label
from typing import Literal, Any, Callable

from models.cliente import Cliente
from models.topicos import topicosMOM

CallbackOnMessage = Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None]
TipoSensor = Literal["Temperatura", "Humidade", "Velocidade"]

def TELA_ATIVO(qtdSensor: int): return f"500x{300 + 20 * qtdSensor}"

class GuiCliente:
  def __init__(self, cliente: Cliente, raiz: Tk):
    self.raiz = raiz
    self.cliente = cliente
    self.sensoresInscritos = []

  def inicializaCliente(self):
    self.cliente.inscreverTopico(topicosMOM.mudanca_topico)
    
    thread_client = Thread(target=self.cliente.inicializaCliente, args=[self.onMessageClient()], daemon=True)
    thread_client.start()

  def atualizaTopicos(self, inicio=False, remove: str = None):
    if remove != None:
      i = int(remove)
      lbl = self.listLblAssinados[i]
      if lbl != None:
        self.listLblAssinados[i].destroy()
      self.listLblAssinados.pop(i)
      selecionados: list[int] = list(self.lbxSensores.curselection())
      for idx in selecionados:
        if idx == i:
          self.lbxSensores.selection_clear(idx)
        elif idx > i:
          self.lbxSensores.selection_clear(idx)
          self.lbxSensores.selection_set(idx - 1)


    lstTopicos = []
    for topico in topicosMOM.topicos:
      sensor = topico.split("/")[1]
      lstTopicos.append(sensor)
      if inicio or len(topicosMOM.topicos) > len(self.listLblAssinados):
        self.listLblAssinados.append(None)

    self.onselect()
    
    self.varTopicos.set(value=lstTopicos)

  def onselect(self):
    try:
      selecionados: list[int] = list(self.lbxSensores.curselection())

      indice = 0
      for index in range(len(topicosMOM.topicos)):
        topico = topicosMOM.topicos[index]
        if index in selecionados:
          self.cliente.inscreverTopico(topico)
          if self.listLblAssinados[index] == None:
            self.listLblAssinados[index] = Label(self.janela, text=topico.split("/")[1], style="Peq.Label")
          self.listLblAssinados[index].place(x=260, y=70 + (indice * 15))
          indice += 1

        else:
          self.cliente.desinscrever(topico)
          if self.listLblAssinados[index] != None:
            self.listLblAssinados[index].destroy()
            self.listLblAssinados[index] = None
    except Exception as e:
      print(f"ERRO onselect: {e}")
      return False

  def onMessageClient(self) -> CallbackOnMessage:
    def onMessageFunc(cli: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
      msg = message.payload.decode()
      topico = message.topic

      if topico.endswith("topics_change"):
        if msg.startswith("remove"):
          self.atualizaTopicos(remove=msg.split(":")[1])
        else:
          self.atualizaTopicos()
      elif topico.startswith("critic"):
        indexTpc = topicosMOM.topicos.index(topico.split("critic")[1])
        self.listLblAssinados[indexTpc].configure(text=f"{topico.split("/")[1]}: {msg}", style="Err.Label")
      else:
        indexTpc = topicosMOM.topicos.index(topico)
        self.listLblAssinados[indexTpc].configure(text=f"{topico.split("/")[1]}: {msg}", style="Peq.Label")
    
    return onMessageFunc

  def criaComponenteJanela(self):
    self.janela = Toplevel(self.raiz)
    self.janela.title("IoT - CLiente MOM")
    self.janela.geometry(TELA_ATIVO(0))
    self.janela.resizable(False, False)

  def criaComponenteEstilos(self):
    self.fonteGeral = Font(size=12, family="Trebuchet MS")
    self.fonteLeitura = Font(size=9, family="Trebuchet MS")

    style = Style()
    style.configure("Gen.Label", font=self.fonteGeral)
    style.configure("Peq.Label", font=self.fonteLeitura)
    style.configure("Err.Label", font=self.fonteLeitura, foreground="#F02424")
    style.configure("NSensor.TButton", width=11, font=self.fonteGeral)
    style.configure("NCliente.TButton", width=12, font=self.fonteGeral)
    style.configure("Sensor.TButton", width=12, font=self.fonteGeral)

  def criaInicilizadorCliente(self):
    self.varTopicos = StringVar(value=[])
    self.varNomeSensor = StringVar()
    self.varLeituras: list[StringVar] = []

    yscrollbar = Scrollbar(self.janela) 
  
    self.listLblAssinados: list[Label | None] = []
    self.lblNomeCliente = Label(self.janela, text=f"Cliente: {self.cliente.nome}", style="Gen.Label")
    self.lblAssinarSensores = Label(self.janela, text="Assinar sensores", style="Gen.Label")
    self.lblInfoAssinados = Label(self.janela, text="Sensores assinados", style="Gen.Label")

    self.lbxSensores = Listbox(
      self.janela,
      selectmode="multiple",
      width=34,
      height=10,
      font=self.fonteLeitura,
      yscrollcommand=yscrollbar.set,
      listvariable=self.varTopicos,
    )

    self.lblNomeCliente.place(x=30, y=10 )
    self.lblAssinarSensores.place(x=30, y=50)
    self.lblInfoAssinados.place(x=260, y=50)

    self.lbxSensores.place(x=30, y=70)
    yscrollbar.place(x=236, y=70, height=3+ 10 * 19, width=17)
    yscrollbar.configure(command=self.lbxSensores.yview)

    self.lbxSensores.bind('<<ListboxSelect>>', lambda _: self.onselect())


  def iniciaAplicacao(self):
    self.criaComponenteJanela()
    self.criaComponenteEstilos()
    self.criaInicilizadorCliente()
    self.atualizaTopicos(inicio=True)
    self.inicializaCliente()
