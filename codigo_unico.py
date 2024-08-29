import paho.mqtt.client as mqtt
from typing import Callable, Any, Literal
from threading import Thread

# models/publisher.py
broker = "localhost"
port = 1883

sensorPublisher = mqtt.Client()
sensorPublisher.connect(broker, port)

# models/cliente.py

class Cliente:
  def __init__(self, nome: str) -> None:
    self.nome = nome

    self.client = mqtt.Client()
    self.client.connect("localhost", 1883)

  def inicializaCliente(self, onMessage) -> None:
    self.client.on_message = onMessage

    self.client.loop_forever()

  def inscreverTopico(self, topico: str):
    self.client.subscribe(topico)
    self.client.subscribe(f"critic{topico}")

  def desinscrever(self, topico: str):
    self.client.unsubscribe(topico)
    self.client.unsubscribe(f"critic{topico}")

# models/sensor.py
TipoSensor = Literal["Temperatura", "Humidade", "Velocidade"]

class Sensor:
  def __init__(
      self,
      tipo,
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

# models/topicos.py
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

# gui/gui_cliente.py

from tkinter import Toplevel, Tk, StringVar, Listbox, Scrollbar, Event
from tkinter.font import Font
from tkinter.ttk import Style, Button, Label, Entry
from typing import Literal, Any, Callable

TipoSensor = Literal["Temperatura", "Humidade", "Velocidade"]

TELA_CLI_ATIVO = "500x300"

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

  def onMessageClient(self):
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
    self.janela.geometry(TELA_CLI_ATIVO)
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

# gui/gui_sensor.py

TELA_INSTANCIANDO = "270x270"
TELA_SENSOR_ATIVO = "330x180"

class GuiSensor:
  def __init__(self, tipoSensor, raiz: Tk):
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
    self.janela.geometry(TELA_SENSOR_ATIVO)
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

# gui/gui_principal.py

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

  def adicionarSensor(self, tipo) -> bool:
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

# index.py

from gui.gui_principal import GuiObjectBuilder

mainGui = GuiObjectBuilder()
mainGui.iniciaAplicacao()
