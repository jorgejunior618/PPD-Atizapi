import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from tkinter import Toplevel, Tk, StringVar
from tkinter.font import Font
from tkinter.ttk import Style, Button, Label, Entry
from typing import Literal

from models.sensor import Sensor
from models.topicos import topicosMOM

TipoSensor = Literal["Temperatura", "Humidade", "Velocidade"]

TELA_INSTANCIANDO = "270x270"
TELA_ATIVO = "330x180"

class GuiSensor:
  def __init__(self, tipoSensor: TipoSensor, raiz: Tk):
    self.tipo = tipoSensor
    self.raiz = raiz
    self.sensor = None

  def onClose(self):
    if self.sensor != None:
      topicosMOM.removerTopico(f"{self.tipo}-{self.sensor.nome}")
    self.janela.destroy()
    

  def criaComponenteJanela(self):
    self.janela = Toplevel(self.raiz)
    self.janela.title("IoT - Sensor MOM")
    self.janela.geometry(TELA_INSTANCIANDO)
    self.janela.resizable(False, False)
    self.janela.protocol("WM_DELETE_WINDOW", self.onClose)

  def criaComponenteEstilos(self):
    self.fonteGeral = Font(size=12, family="Trebuchet MS")
    self.fonteLeitura = Font(size=9, family="Trebuchet MS")

    style = Style()
    style.configure(
      "Gen.Label",
        font=self.fonteGeral,
      )
    style.configure(
      "Err.Label",
        font=self.fonteLeitura,
        foreground="#F02424"
      )
    style.configure(
      "Leitura.Label",
        font=self.fonteLeitura
      )
    style.configure(
      "NSensor.TButton",
        width=11,
        font=self.fonteGeral
      )
    style.configure(
      "NCliente.TButton",
        width=12,
        font=self.fonteGeral
      )
    style.configure(
      "Sensor.TButton",
        width=12,
        font=self.fonteGeral
      )

  def criaInicilizadorSensor(self):
    self.varNomeSensor = StringVar()
    self.varValor = StringVar()
    self.varLimMin = StringVar()
    self.varLimMax = StringVar()

    self.lblTipoSensor = Label(self.janela, text=f"Sensor de {self.tipo}:", style="Gen.Label")
    self.lblLimMin = Label(self.janela, text="Limíte mínimo do sensor", style="Gen.Label")
    self.lblLimMax = Label(self.janela, text="Limíte máximo do sensor", style="Gen.Label")
    self.lblErroNome = Label(self.janela, text="", style="Err.Label")
    self.lblNomeSensor = Label(self.janela, text="Nome do novo Sensor", style="Gen.Label")

    self.inputLimMin = Entry(self.janela, textvariable=self.varLimMin, width=16, font=self.fonteGeral)
    self.inputLimMax = Entry(self.janela, textvariable=self.varLimMax, width=16, font=self.fonteGeral)
    self.inputNome = Entry(self.janela, textvariable=self.varNomeSensor, width=16, font=self.fonteGeral)

    self.botInstanciaSensor = Button(self.janela, text="Criar", command=self.instanciarSensor, style="NSensor.TButton")
  
    self.lblTipoSensor.place(x=30, y=10)
    self.lblLimMin.place(x=30, y=50)
    self.lblLimMax.place(x=30, y=100)
    self.lblErroNome.place(x=30, y=155)
    self.lblNomeSensor.place(x=30, y=170)

    self.inputLimMin.place(x=30, y=70)
    self.inputLimMax.place(x=30, y=120)
    self.inputNome.place(x=30, y=190)

    def bindEnterMin(kc):
      if kc == 13: # Pressionou enter
        self.inputLimMax.focus()
    def bindEnterMax(kc):
      if kc == 13: # Pressionou enter
        self.inputNome.focus()
    def bindEnterNome(kc):
      if kc == 13: # Pressionou enter
        self.instanciarSensor()
    self.inputLimMin.focus()
    self.inputLimMin.bind("<Key>", lambda e: bindEnterMin(e.keycode))
    self.inputLimMax.bind("<Key>", lambda e: bindEnterMax(e.keycode))
    self.inputNome.bind("<Key>", lambda e: bindEnterNome(e.keycode))

    self.botInstanciaSensor.place(x=30, y=220)

  def criaComponentesSensorAtivo(self):
    self.janela.geometry(TELA_ATIVO)
    self.lblTopicoSensor = Label(self.janela, textvariable=self.varNomeSensor, style="Gen.Label")
    self.lblModValor = Label(self.janela, text="Atualize o valor do sensor", style="Gen.Label")
    self.lblLeitura = Label(self.janela, text="Leitura atual:", style="Leitura.Label")
    self.lblLeituraMin = Label(
      self.janela,
      text=f"Mín: {self.varLimMin.get()}",
      style="Gen.Label",
      foreground="#6363FE"
    )
    self.lblLeituraMax = Label(
      self.janela,
      text=f"Max: {self.varLimMax.get()}",
      style="Gen.Label",
      foreground="#DF8004"
    )
    self.lblLeituraAtual = Label(self.janela, textvariable=self.varLeitura, style="Leitura.Label")

    self.inputValor = Entry(self.janela, textvariable=self.varValor, width=16, font=self.fonteGeral)

    self.botModValor = Button(self.janela, text="Atualizar", command=self.modValor, style="NSensor.TButton")
  
    self.lblTopicoSensor.place(x=205, y=10)
    self.lblModValor.place(x=30, y=60)
    self.lblLeitura.place(x=30, y=118)
    self.lblLeituraAtual.place(x=110, y=118)

    self.lblLeituraMin.place(x=30, y=140)
    self.lblLeituraMax.place(x=100, y=140)

    self.inputValor.place(x=30, y=90)
    self.inputValor.focus()

    self.botModValor.place(x=170, y=88)

    def bindEnter(kc):
      if kc == 13: # Pressionou enter
        self.modValor()
    self.inputValor.bind("<Key>", lambda e: bindEnter(e.keycode))

  def removeComponentesInicilizador(self):
    self.lblLimMin.destroy()
    self.lblLimMax.destroy()
    self.lblNomeSensor.destroy()
    self.lblErroNome.destroy()

    self.inputLimMin.destroy()
    self.inputLimMax.destroy()
    self.lblErroNome.destroy()
    self.inputNome.destroy()

    self.botInstanciaSensor.destroy()

  def instanciarSensor(self):
    self.varLeitura = StringVar()
    try:
      nomeSensor = self.varNomeSensor.get()
      minSensor = self.varLimMin.get()
      maxSensor = self.varLimMax.get()
      self.sensor = Sensor(tipo=self.tipo, nome=nomeSensor, min=float(minSensor), max=float(maxSensor))

      self.varLeitura.set(f"{self.sensor.valor}")
      if topicosMOM.adicionarTopico(f"{self.tipo}-{self.sensor.nome}"):
        self.removeComponentesInicilizador()
        self.criaComponentesSensorAtivo()
      else:
        self.lblErroNome.config(text="Nome ja utilizado")

    except Exception as e:
      print("erro instanciarSensor: ", e)

  def modValor(self) -> bool:
    try:
      novoValor = float(self.varValor.get())
      valMin = float(self.varLimMin.get())
      valMax = float(self.varLimMax.get())
      self.sensor.setValor(novoValor)

      self.varLeitura.set(novoValor)
      if novoValor <= valMin or novoValor >= valMax:
        self.lblLeituraAtual.configure(foreground="#F02424")
      else:
        self.lblLeituraAtual.configure(foreground="#000000")
    except Exception as e:
      print("erro modValor: ", e)

  def iniciaAplicacao(self):
    self.criaComponenteJanela()
    self.criaComponenteEstilos()
    self.criaInicilizadorSensor()
