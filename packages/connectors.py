import packages.aistudio as aistudio
import packages.listeners as listeners
import packages.audioparser as audioparser
from packages.listeners import getPrivateIp

import tempfile
import json
import os
import socket
import copy
import hashlib

import dotenv
env = dotenv.dotenv_values()

LLM_PORT = 8801
PROFL_PORT = 8802
AUDESC_PORT = 8803
LLM_DATA_SPLITTER = bytearray([1,1,1,1])

class llmServerSide:
    def __init__(self):
        self.studio = aistudio.AIStudio(env['apikey'])
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
        
    def prepare_chat(self, profile: dict) -> aistudio.Chat:
        if profile['credentials']['username'] in self.chats:
            chat = self.chats[profile['credentials']['username']]
        else:
            chat = self.studio.get_chat(self.studio.gemini25flash)
            self.chats[profile['credentials']['username']] = chat
        sysinstructions = "You are an AI to help children with different forms of autism in moments of stress or panic to calm down. Only include one question and a couple of sentences per response. You are not able to do any function calls like calling phones. You are able to put hyperlinks to phone numbers in the response by inserting \'<a href=\"tel:[number]\">[text]</a>\'. Get to the point of solving the problem, and not just providing calming strategies. Child profile: " + json.dumps(profile)
        chat.set_system_instructions(sysinstructions)
        return chat

    def onmessage(self, conn: socket.socket, data: bytes):
        parts = data.split(LLM_DATA_SPLITTER)
        profile = json.loads(parts[0])
        chat = self.prepare_chat(profile)

        query = parts[1].decode('utf-8')
        conn.send(self.startStreamPckt)
        for part in chat.prompt(query):
            conn.send(part.encode())
        conn.send(self.stopStreamPckt)
        with open(self.filepath, "a") as f:
            f.write(f"{conn.getpeername()}: Query from {profile['credentials']['username']}:\n\n{query}")

    def onclose(self, addr):
        self.log(f"{addr}: Connection closed")

    def onerror(self, conn: socket.socket, e: Exception):
        self.log(f"{conn.getpeername()}: Exception in connection: {e}")
        #raise

class llmClientSide:
    def __init__(self, profile, host):
        self.profile = profile
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
        payload = json.dumps(self.profile).encode() + LLM_DATA_SPLITTER + query.encode()
        self.sclient.send(payload)

class profilesServerSide:
    def __init__(self):
        self.sserver = listeners.createListener(PROFL_PORT)

        self.logInPcktType = 2
        self.logInAcceptPckt = 5
        self.errorPcktType = 4
        self.signupFinishedPcktType = 6

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
            with open(profile_path)as f:
                profile = json.loads(f.read())
                if hashlib.sha256(password.encode()).hexdigest() == profile["credentials"]["password"]:
                    conn.send(bytearray([self.logInAcceptPckt])+json.dumps(profile).encode())
                else:
                    conn.send(bytearray([self.errorPcktType])+b"Invalid password")
        else:
            conn.send(bytearray([self.errorPcktType])+b"Profile does not exist. Please create a profile first.")

    def onSignUp(self, conn: socket.socket, profile):
        profile_path = os.path.join("user_profiles", f"{profile['credentials']['username']}.json")
        if os.path.exists(profile_path):
            conn.send(bytearray([self.errorPcktType])+b"Username is taken")
        else:
            with open(profile_path, "w+")as f:
                profile2 = copy.copy(profile)
                profile2["credentials"] = {
                    "username" : profile2["credentials"]["username"],
                    "password" : profile2["credentials"]["passwordhash"]
                }
                f.write(json.dumps(profile))
                conn.send(bytearray([self.signupFinishedPcktType]))
                

    def onopen(self, conn: socket.socket):
        self.log(f"Connection from {conn.getpeername()}")

    def onmessage(self, conn: socket.socket, data: bytes):
            logging_in = data[0] == self.logInPcktType
            data = json.loads(data[1:])
            if not logging_in:
                required_keys = {
                    "credentials": ['username", "password'],
                    "general": ['first_name", "last_name", "gender", "dob'],
                    "diagnosis": ['autism_type", "communication_styles'],
                    "calming": ['image_themes", "sound_themes", "techniques'],
                    "triggers": ['anxieties", "sensitivities'],
                    "emergency": ['primary_contact_name", "relationship", "phone", "gps']
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

                if not isinstance(data['diagnosis']['communication_styles'], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                if not isinstance(data['calming']['image_themes'], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                if not isinstance(data['calming']['sound_themes'], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                if not isinstance(data['triggers']['anxieties'], list):
                    conn.send(bytearray([self.errorPcktType])+b"Invalid profile")
                data['credentials']['passwordhash'] = hashlib.sha256(data['credentials']['password'].encode()).hexdigest()
                self.onSignUp(conn, data)
            else:
                if (not "username" in data) or (not "password" in data):
                    self.log(f"{conn.getpeername()}: Login attempt: did not provide credentials")
                    conn.send(bytearray([self.errorPcktType])+b"Please provide username and password")
                else:
                    self.log(f"{conn.getpeername()}: Login attempt: USER = {data['username']}, PWD = {data['password']}")
                    self.onAttemptLogIn(conn, data['username'], data['password'])

    def onclose(self, addr):
        self.log(f"{addr}: Connection closed")

    def onerror(self, conn: socket.socket, e: Exception):
        self.log(f"{conn.getpeername()}: Exception in connection: {e}")

class profilesClientSide:
    def __init__(self, host):
        self.sclient = listeners.connectToListener(host, PROFL_PORT)
        self.logInPcktType = 2
        self.signUpPcktType = 3
        self.errorPcktType = 4
        self.logInAcceptPcktType = 5
        self.signupFinishedPcktType = 6

        self.sclient.onmessage = self.onmessage

        self.onGotProfile = lambda profile:None
        self.onSignupSuccess = lambda:None
        self.onClientError = lambda error:None

        if not self.sclient.running:
            raise Exception("Server is offline")
        
    def onmessage(self, conn: socket.socket, data):
        if data[0] == self.errorPcktType:
            self.onClientError(data[1:].decode())
        elif data[0] == self.logInAcceptPcktType:
            self.onGotProfile(json.loads(data[1:]))
        elif data[0] == self.signupFinishedPcktType:
            self.onSignupSuccess()

    def log_in(self, username, password):
        self.sclient.send(bytearray([self.logInPcktType])+json.dumps({"username":username,"password":password}).encode())

    def sign_up(self, profile):
        self.sclient.send(bytearray([self.signUpPcktType])+json.dumps(profile).encode())


class audioDescServerSide:
    def __init__(self, llmss):
        self.llmss = llmss
        self.sserver = listeners.createListener(AUDESC_PORT)

        self.describeRequest = 2
        self.describeResponse = 3

        self.recieving = False

        self.sserver.onopen = self.onopen
        self.sserver.onmessage = self.onmessage
        self.sserver.onclose = self.onclose
        self.sserver.onerror = self.onerror

    def start(self):
        self.sserver.start()

    def log(self, text: str):
        print("[+] AUDESC Service: "+text)

    def onopen(self, conn: socket.socket):
        self.log(f"Connection from {conn.getpeername()}")

    def onmessage(self, conn: socket.socket, data: bytes):
        self.log(f"{conn.getpeername()}: Got data")
        isRequest = data[0] == self.describeRequest
        if isRequest or self.recieving:
            tmpfile = tempfile.mktemp(".wav", "tmp", tempfile.gettempdir())
            with open(tmpfile, "wb") as f:
                f.write(data[1:])
                print(data)
            conn.send(bytearray([self.describeResponse])+audioparser.describe(self.llmss.studio, tmpfile))
            print("Sent description")

    def onclose(self, addr):
        self.log(f"{addr}: Connection closed")

    def onerror(self, conn: socket.socket, e: Exception):
        self.log(f"{conn.getpeername()}: Exception in connection: {e}")

class audioDescClientSide:
    def __init__(self, host):

        self.sclient = listeners.connectToListener(host, AUDESC_PORT)
        self.describeRequest = 2
        self.describeResponse = 3

        self.sclient.onmessage = self.onmessage

        if not self.sclient.running:
            raise Exception("Server is offline")
        
    def gotAudioDescription(self, description: str):
        pass

    def onmessage(self, conn: socket.socket, data: bytes):
        isResponse = data[0] == self.describeResponse
        if isResponse:
            self.gotAudioDescription(data[1:].decode())
    
    def describe(self, audiofile):
        with open(audiofile, "rb")as f:
            self.sclient.send(bytearray([self.describeRequest])+f.read())