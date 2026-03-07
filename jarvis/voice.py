import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel("base", compute_type="int8")

def record_audio(duration=4):

    samplerate = 16000

    print("Слушаю...")

    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    return audio.flatten()

def speech_to_text():

    try:

        audio = record_audio()

        segments, info = model.transcribe(audio)

        text = ""

        for segment in segments:
            text += segment.text

        return text.strip()

    except KeyboardInterrupt:

        print("Остановка записи")

        return ""