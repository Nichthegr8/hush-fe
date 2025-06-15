from google import genai
from google.genai.types import Content, Part, GenerateContentConfig

import os
import copy

def hookGenerator(func, generator):
    for i in generator:
        func(i)
        yield i

class Chat:
    def __init__(self, client: genai.Client, model: str):
        self.client=client
        self.model = model
        self.contents: list[Content] = []

    def set_system_instructions(self, instructions):
        instructions = Content(
            role="system",
            parts=[
                Part(text=instructions)
            ]
        )
        if len(self.contents) == 0:
            self.contents = [instructions]
        elif self.contents[0].role != "system":
            self.contents = [instructions] + self.contents
        elif self.contents[0].role == "system":
            self.contents[0] = instructions

    def clear(self):
        self.contents = []

    def prompt(self, prompt):
        self.contents += [
            Content(
                role="user",
                parts=[
                    Part(text = prompt)
                ]
            )
        ]
        contents = copy.copy(self.contents)
        sysinstructions = None
        if contents[0].role != "user":
            sysinstructions = contents[0].parts[0].text
            contents=contents[1:]

        generator = (i.text for i in hookGenerator((
            lambda streamPart: self.addToContentText(
                streamPart.text
            )
            ), self.client.models.generate_content_stream(
            model = self.model, 
            contents = contents,
            config=GenerateContentConfig(
                system_instruction=sysinstructions
            )
        )))

        self.contents += [
            Content(
                role="model",
                parts=[
                    Part(text = "")
                ]
            )
        ]

        return generator

    def addToContentText(self, add):
        try:
            self.contents[-1].parts[0].text += add
        except:
            pass

    @property
    def history(self) -> list[Content]:
        return self.contents

    @property 
    def system_instructions(self) -> str:
        if len(self.contents) == 0:
            return
        if self.contents[0].role != "system":
            return None
        else:
            return self.contents[0].parts[0].text

class AIStudio:
    def __init__(self, apikey: str = None):
        if not apikey:
            apikey=os.environ["apikey"]
        print("Loading client")
        self.client = genai.Client(api_key=apikey)
        print("Loaded")
        self.gemini25flash = "gemini-2.5-flash-preview-05-20"
    def query_llm(self, prompt, model = "gemini-2.5-flash-preview-05-20"):
        self.client.models.generate_content_stream(
            model = model,
            contents = [
                Content(
                    role="user",
                    parts=[
                        Part(text=prompt)
                    ]
                )
            ]
        )
    def get_chat(self, model):
        return Chat(self.client, model)

def set_apikey(api_key: str):
    os.environ["apikey"] = api_key

if __name__ == "__main__":
    studio = AIStudio(apikey=os.environ["apikey"])
    chat = studio.get_chat(studio.gemini25flash)

    with open("data/profile.json")as f:
        profile = f.read()

    sysinstructions = "You are an AI to help children with different forms of autism in moments of stress or panic to calm down. Only include one question and a couple of sentences per response. Get to the point of solving the problem the user adresses and don't digress or get sidetracked, even if the profile's calming techniques includes stuff like distractions. Child profile: " + profile
    chat.set_system_instructions(sysinstructions)

    while True:
        for part in chat.prompt(input(">>>")):
            print(part, end="", flush=True)
        print()