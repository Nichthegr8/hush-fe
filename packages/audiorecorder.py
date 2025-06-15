import pyaudio
import wave
import threading

class Recorder:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.recording = False
        self.frames = []
        self.p = None
        self.stream = None
        self.thread = None

    def start_recording(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        self.recording = True
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def stop_recording(self):
        self.recording = False
        if self.thread:
            self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        frames = self.frames
        self.frames = []
        return frames

    def record(self):
        while self.recording:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            self.frames.append(data)

    def frames_to_file(self, frames: list, file: str):
        if not file.endswith(".wav"):
            file = file+".wav"
            print("Warning (audio.Recorder.record): file must end in .wav, new file name:",file)
        with wave.open(file, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
        with open(file, 'rb') as f:
            print(f.read())