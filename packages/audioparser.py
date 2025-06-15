import dotenv
import shutil
dotenv.load_dotenv()

def describe(ais, audio_file):
    file = ais.client.files.upload(file=audio_file)
    shutil.copyfile(audio_file, "test.wav")
    content = ais.client.models.generate_content(
        model = ais.gemini25flash, 
        contents = [
            "Describe this audio, in the format \"In this audio, the user is saying xxxx. In the background you can hear xxxx\"",
            file
        ]
    ).text
    return content