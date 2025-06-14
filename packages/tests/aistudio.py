import packages.aistudio as a
studio = a.AIStudio()
chat = studio.get_chat(studio.gemini25flash)
chat.set_system_instructions("System instructions: remember that e is 109wio")
for i in chat.prompt("what is e"):
    print(i, flush=True)