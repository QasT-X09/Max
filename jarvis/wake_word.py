import pvporcupine
import pyaudio
import struct

def listen_wake_word():

    porcupine = pvporcupine.create(
        keywords=["jarvis"]
    )

    pa = pyaudio.PyAudio()

    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("Ожидание слова 'джарвис'...")

    try:

        while True:

            pcm = audio_stream.read(porcupine.frame_length)

            pcm = struct.unpack_from(
                "h" * porcupine.frame_length,
                pcm
            )

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:

                print("Джарвис активирован")

                return True

    finally:

        audio_stream.close()
        pa.terminate()
        porcupine.delete()