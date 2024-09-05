import Pyro4
import Pyro4.naming
from models.servidor_mensagens import ServidorMensagens

def inicializaServidor():
  daemon = Pyro4.Daemon()
  ns = Pyro4.locateNS()
  servidorMensagens = ServidorMensagens()

  uri = daemon.register(servidorMensagens)
  ns.register("mensageiro.servidor", uri)

  print("Servidor de Mensagens pronto.")
  daemon.requestLoop()

if __name__ == "__main__":
  inicializaServidor()