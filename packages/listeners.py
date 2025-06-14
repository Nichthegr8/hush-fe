import packages.sockcomm as sc
import socket

def getPrivateIp():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def createListener(port: int = 8801):
    return sc.socketServer("0.0.0.0", port)

def connectToListener(host: str, port: int):
    socketclient = sc.socketClient(host, port)
    socketclient.connect()
    return socketclient
