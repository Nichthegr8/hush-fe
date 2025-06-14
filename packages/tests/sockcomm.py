import packages.sockcomm as sc

host="127.0.0.1"
port=8001

sserv = sc.socketServer(host, port)


def onopen(comm):
    ...