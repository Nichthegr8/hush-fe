import packages.aistudio as aistudio
import packages.geolocation as geolocation
import packages.listeners as listeners
from packages.listeners import getPrivateIp

import json
import os
import socket
import hashlib

import dotenv
env = dotenv.dotenv_values()

LLM_PORT = 8801
PROFL_PORT = 8802
LLM_DATA_SPLITTER = bytearray([1,1,1,1])

class llmServerSide:
    def __init__(self):
        self.studio = aistudio.AIStudio(env["apikey"])
        self.chats: dict[str, aistudio.Chat] = {}

        self.sserver = listeners.createListener(LLM_PORT)
        self.filepath = os.path.join(os.getcwd(), "logs/llm.log")
        self.startStreamPckt = bytearray([2])
        self.stopStreamPckt = bytearray([3])

        self.sserver.onopen = self.onopen
        self.sserver.onmessage = self.onmessage
        self.sserver.onclose = self.onclose
        self.sserver.onerror = self.onerror

    def start(self):
        self.sserver.start()

    def log(self, text: str):
        print("[+] LLM Service: "+text)

    def onopen(self, conn: socket.socket):
        self.log(f"Connection from {conn.getpeername()}")

    def load_profile(self, name: str):
        if not name in self.chats:
            return {}
        with open(os.path.join(os.getcwd(), "user_profiles", f"{name}.json"))as f:
            return f.read()
        
    def prepare_chat(self, name: str) -> aistudio.Chat:
        if name in self.chats:
            chat = self.chats[name]
        else:
            chat = self.studio.get_chat(self.studio.gemini25flash)
            self.chats[name] = chat
        profile = self.load_profile(name)
        location = json.dumps(geolocation.getUserLocation())
        sysinstructions = "You are an AI to help children with different forms of autism in moments of stress or panic to calm down. Only include one question and a couple of sentences per response. Get to the point of solving the problem the user adresses and don't digress or get sidetracked, even if the profile's calming techniques includes stuff like distractions. Child profile: " + profile + ". Child location: " + location
        chat.set_system_instructions(sysinstructions)
        return chat

    def onmessage(self, conn: socket.socket, data: bytes):
        parts = data.split(LLM_DATA_SPLITTER)
        child = parts[0]
        chat = self.prepare_chat(child.decode())

        query = parts[1].decode('utf-8')
        conn.send(self.startStreamPckt)
        for part in chat.prompt(query):
            conn.send(part.encode())
        conn.send(self.stopStreamPckt)
        with open(self.filepath, "a") as f:
            f.write(f"{conn.getpeername()}: Query from {child}:\n\n{query}")

    def onclose(self, addr):
        self.log(f"{addr}: Connection closed")

    def onerror(self, conn: socket.socket, e: Exception):
        self.log(f"{conn.getpeername()}: Exception in connection: {e}")

class llmClientSide:
    def __init__(self, name, host):
        self.name = name
        self.startStreamPckt = 2
        self.stopStreamPckt = 3

        self.sclient = listeners.connectToListener(host, LLM_PORT)
        self.sclient.onmessage = self.onmessage

        if not self.sclient.running:
            raise Exception("Server is offline")

        self.streamstarted = False
    
    def addToStream(self, streampart: str):
        pass

    def onendstream(self):
        pass

    def onstartstream(self):
        pass

    def onmessage(self, conn: socket.socket, message: bytes):
        pckttype = message[0]
        if pckttype == self.startStreamPckt:
            self.streamstarted = True
        elif pckttype == self.stopStreamPckt:
            self.streamstarted = False
        else:
            if self.streamstarted:
                self.addToStream(message.decode())

    def generate_response(self, query: str):
        payload = self.name.encode() + LLM_DATA_SPLITTER + query.encode()
        self.sclient.send(payload)


class profilesServerSide:
    def __init__(self):
        self.sserver = listeners.createListener(PROFL_PORT)

        self.logInPcktType = 2
        self.errorPcktType = 4

        self.sserver.onopen = self.onopen
        self.sserver.onmessage = self.onmessage
        self.sserver.onclose = self.onclose
        self.sserver.onerror = self.onerror

    def start(self):
        self.sserver.start()

    def log(self, text: str):
        print("[+] PROFL Service: "+text)

    def onAttemptLogIn(self, conn: socket.socket, username, password):
        profile_path = os.path.join("user_profiles", f"{username}.json")
        if os.path.exists(profile_path):
            pass
        else:
            conn.send(bytearray([self.errorPcktType])+b"")

    def onSignUp(self, profile):
        pass

    def onopen(self, conn: socket.socket):
        self.log(f"Connection from {conn.getpeername()}")

    def onmessage(self, conn: socket.socket, data: bytes):
        try:
            logging_in = data[0] == self.logInPcktType
            data = json.loads(data[1:])
            if not logging_in:
                required_keys = {
                    "credentials": ["username", "password"],
                    "general": ["first_name", "last_name", "gender", "dob"],
                    "diagnosis": ["autism_type", "communication_styles"],
                    "calming": ["image_themes", "sound_themes", "techniques"],
                    "triggers": ["anxieties", "sensitivities"],
                    "emergency": ["primary_contact_name", "relationship", "phone", "gps"]
                }

                # Check all top-level keys exist
                if not all(key in data for key in required_keys):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")

                # Check all subkeys exist
                for section, subkeys in required_keys.items():
                    if not isinstance(data[section], dict):
                        conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                    for subkey in subkeys:
                        if subkey not in data[section]:
                            conn.send(bytearray([self.errorPcktType])+b"Invalid profile")

                if not isinstance(data["diagnosis"]["communication_styles"], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                if not isinstance(data["calming"]["image_themes"], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                if not isinstance(data["calming"]["sound_themes"], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                if not isinstance(data["triggers"]["anxieties"], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
            else:
                if (not "username" in data) or (not "password" in data):
                    conn.send(bytearray([self.errorPcktType])+b"Please provide username and password")
                else:
                    self.onAttemptLogIn(conn, data["username"], data["password"])
                
        except:
            self.log(f"{conn.getpeername()}: Sent invalid signup or login")
            return
        

        data["credentials"]["passwordhash"] = hashlib.sha256(data["credentials"]["password"].encode()).hexdigest()

    def onclose(self, addr):
        self.log(f"{addr}: Connection closed")

    def onerror(self, conn: socket.socket, e: Exception):
        self.log(f"{conn.getpeername()}: Exception in connection: {e}")

class profilesClientSide:
    def __init__(self, name, host):
        self.name = name

        self.sclient = listeners.connectToListener(host, PROFL_PORT)
        self.logInPcktType = 2
        self.signUpPcktType = 3
        self.errorPcktType = 4

        if not self.sclient.running:
            raise Exception("Server is offline")
        
    def onClientError(self, error: str):
        pass
        
    def onmessage(self, conn: socket.socket, data):
        if data[0] == self.errorPcktType:
            self.onError(data[1:])

    def log_in(self, username, password):
        self.sclient.send(bytearray([self.logInPcktType])+json.dumps({"username":username,"password":password}).encode())

    def sign_up(self, profile):
        self.sclient.send(bytearray([self.signUpPcktType])+json.dumps(profile).encode())