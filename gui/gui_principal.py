import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from tkinter import Tk, StringVar
from tkinter.font import Font
from tkinter.ttk import Style, Button, Label, Entry
from typing import Literal

from gui.gui_sensor import GuiSensor
from gui.gui_cliente import GuiCliente

from models.topicos import topicosMOM
from models.cliente import Cliente

TELA_NORMAL = "270x115"
TELA_NSENSOR = "270x270"
TELA_NCLIENTE = "270x200"

TipoSensor = Literal["Temperatura", "Humidade", "Velocidade"]

class GuiObjectBuilder:
  def __init__(self):
    self.criandoSensor = False
    self.criandoCliente = False

    self.criaComponenteJanela()
    self.criaComponenteEstilos()
    self.criaBotoesBuilder()

  def criaComponenteJanela(self):
    self.janela = Tk()
    self.janela.title("IoT - MOM")
    self.janela.geometry(TELA_NORMAL)
    self.janela.resizable(False, False)

  def criaComponenteEstilos(self):
    self.fonteGeral = Font(size=12, family="Trebuchet MS")
    self.fonteLeitura = Font(size=9, family="Trebuchet MS")

    style = Style()
    style.configure(
      "Gen.Label",
        font=self.fonteGeral
      )
    style.configure(
      "Err.Label",
        font=self.fonteLeitura,
        foreground="#F02424"
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

  def criaBotoesBuilder(self):
    self.varNome = StringVar()

    self.botNovoSensor = Button(self.janela, text="Novo sensor", command=self.criaComponentesNovoSensor, style="NSensor.TButton")
    self.botNovoClinte = Button(self.janela, text="Novo cliente", command=self.criaComponentesNovoCliente, style="NCliente.TButton")
  
    self.botNovoSensor.place(x=30, y=30)
    self.botNovoClinte.place(x=130, y=30)

  def criaComponentesNovoSensor(self):
    if self.criandoSensor:
      self.removeComponentesNovoSensor()
      self.criandoSensor = False
      return
    elif self.criandoCliente:
      self.removeComponentesNovoCliente()
      self.criandoCliente = False

    try:
      self.criandoSensor = True
      self.janela.geometry(TELA_NSENSOR)

      self.lblSelecionarSensor = Label(self.janela, text="Selecione o tipo de sensor \na adicionar", style="Gen.Label")
      self.botSenTemperatura = Button(
        self.janela,
        text="Temperatura",
        command=lambda : self.adicionarSensor("Temperatura"),
        style="Sensor.TButton"
      )
      self.botSenHumidade = Button(
        self.janela,
        text="Humidade",
        command=lambda : self.adicionarSensor("Humidade"),
        style="Sensor.TButton"
      )
      self.botSenVelocidade = Button(
        self.janela,
        text="Velocidade",
        command=lambda : self.adicionarSensor("Velocidade"),
        style="Sensor.TButton"
      )

      self.lblSelecionarSensor.place(x=30, y=75)
      self.botSenTemperatura.place(x=30, y=130)
      self.botSenHumidade.place(x=30, y=170)
      self.botSenVelocidade.place(x=30, y=210)

    except Exception as e:
      print("erro criaComponentesNovoSensor: ", e)

  def removeComponentesNovoSensor(self):
    try:
      self.lblSelecionarSensor.destroy()
      self.botSenTemperatura.destroy()
      self.botSenHumidade.destroy()
      self.botSenVelocidade.destroy()

      self.janela.geometry(TELA_NORMAL)
    except Exception as e:
      print("erro removeComponentesNovoSensor: ", e)
  
  def criaComponentesNovoCliente(self):
    if self.criandoCliente:
      self.removeComponentesNovoCliente()
      self.criandoCliente = False
      return
    elif self.criandoSensor:
      self.criandoSensor = False
      self.removeComponentesNovoSensor()
    try:
      self.criandoCliente = True
      self.janela.geometry(TELA_NCLIENTE)

      self.lblErroNome = Label(self.janela, text="", style="Err.Label")
      self.lblNmCLiente = Label(self.janela, text="Nome do Cliente", style="Gen.Label")
      self.inputNmCli = Entry(self.janela, textvariable=self.varNome, width=16, font=self.fonteGeral)
      self.botCriarCliente = Button(self.janela, text="Adicionar", command=self.adicionarCliente, style="Sensor.TButton")

      self.lblErroNome.place(x=30, y=75)
      self.lblNmCLiente.place(x=30, y=90)
      self.inputNmCli.place(x=30, y=115)
      self.botCriarCliente.place(x=30, y=150)

      self.inputNmCli.focus()
      def bindEnter(kc):
        if kc == 13: # Pressionou enter
          self.adicionarCliente()
      self.inputNmCli.bind("<Key>", lambda e: bindEnter(e.keycode))
      
    except Exception as e:
      print("erro criaComponentesNovoCliente: ", e)

  def removeComponentesNovoCliente(self):
    try:
      self.varNome.set("")
      self.inputNmCli.destroy()
      self.lblNmCLiente.destroy()
      self.botCriarCliente.destroy()
      self.lblErroNome.destroy()

      self.janela.geometry(TELA_NORMAL)
    except Exception as e:
      print("erro removeComponentesNovoCliente: ", e)

  def adicionarSensor(self, tipo: TipoSensor) -> bool:
    try:
      self.removeComponentesNovoSensor()

      sensorGui = GuiSensor(tipo, self.janela)
      sensorGui.iniciaAplicacao()

      self.criandoSensor = False
    except Exception as e:
      return False

  def adicionarCliente(self) -> bool:
    nomeNovoCLiente = self.varNome.get()
    if len(nomeNovoCLiente) < 2:
      self.lblErroNome.configure(text="Nome inválido")
      return False
    if not topicosMOM.adicionarCliente(nomeNovoCLiente):
      self.lblErroNome.configure(text="Nome ja utilizado")
      return False

    try:
      clienteNovo = Cliente(nomeNovoCLiente)
      clienteGui = GuiCliente(cliente=clienteNovo, raiz=self.janela)
      clienteGui.iniciaAplicacao()

      self.removeComponentesNovoCliente()
      self.criandoCliente = False
    except Exception as e:
      print(f"ERRO adicionarCliente: {e}")
      return False
    return True

  def iniciaAplicacao(self):
    self.janela.mainloop()
