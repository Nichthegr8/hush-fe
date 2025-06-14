import socket
import threading

def getaddr(conn):
    return conn.getpeername()

class socketServer():
    def __init__(self, host:str="0.0.0.0", port:int=8001):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))

    def start(self):
        self.s.listen()
        print(f"Listening on {self.host}:{self.port}")
        threading.Thread(target=self.waitForClients).start()

    def onopen(self, conn: socket.socket):
        pass
    def onmessage(self, conn: socket.socket, data: bytes):
        pass
    def onclose(self, conn: socket.socket):
        pass
    def onerror(self, conn: socket.socket, e: Exception):
        pass
    
    def waitForClients(self):
        while True:
            conn, addr = self.s.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn: socket.socket, addr):
        self.onopen(conn)
        try:
            with conn:
                while True:
                    try:
                        data = conn.recv(1024)
                        if not data:
                            break
                        self.onmessage(conn, data)
                    except Exception as e:
                        self.onerror(conn, e)
                        break
        except Exception as e:
            self.onerror(conn, e)
        finally:
            self.onclose(conn)

class socketClient():
    def __init__(self, host: str = "127.0.0.1", port: int = 8801):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def connect(self):
        try:
            self.s.connect((self.host, self.port))
            self.addr = self.s.getpeername()
            self.running = True
            threading.Thread(target=self.listen).start()
            self.onopen(self.s)
        except Exception as e:
            self.onerror(self.s, e)

    def send(self, data: bytes):
        try:
            self.s.sendall(data)
        except Exception as e:
            self.onerror(self.s, e)

    def close(self):
        self.running = False
        try:
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close(self)
        except Exception as e:
            self.onerror(self.s, e)
        finally:
            self.onclose(self.addr)

    def listen(self):
        try:
            while self.running:
                try:
                    data = self.s.recv(1024)
                    if not data:
                        break
                    self.onmessage(self.s, data)
                    #print(f"[+] sockcomm.py: function call: self.onmessage({data})")
                except Exception as e:
                    self.onerror(self.s, e)
                    break
        finally:
            self.close()

    def onopen(self, conn: socket.socket):
        pass

    def onmessage(self, conn: socket.socket, data: bytes):
        pass

    def onclose(self, addr: tuple[str, int]):
        pass

    def onerror(self, conn: socket.socket, e: Exception):
        pass