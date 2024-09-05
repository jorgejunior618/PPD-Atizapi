import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from tkinter import Tk, StringVar
from tkinter.font import Font
from tkinter.ttk import Style, Button, Label, Entry

from gui.gui_cliente import GuiCliente

from models.cliente import Cliente
from models.i_serv_mensagens import servidorMensagens

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
