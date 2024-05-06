import os
import wave
from vosk import Model, KaldiRecognizer, SetLogLevel
import pyaudio
from pydub import AudioSegment
import threading
from diarize import transcribe

who_sad_first = 'студент'
num_speakers = int(input('Введите количество говорящих: '))
SetLogLevel(-1)
model = Model(r"vosk-model-small-ru-0.22")
recognizer = KaldiRecognizer(model, 16000)
sample_width = 2
output_rate = 16000
output_channels = 1
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=32768)
stream.start_stream()
print("Говорите")
count = 0


while True:
    data = stream.read(32768, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        text = recognizer.Result()
        if text[14:-3] != '':
            count += 1
            output_filename = f"звуковая_запись{count}.wav"
            wf = wave.open(output_filename, 'wb')
            wf.setnchannels(output_channels)
            wf.setsampwidth(mic.get_sample_size(pyaudio.paInt16))
            wf.setframerate(output_rate)
            wf.writeframes(data=data)
            wf.close()
            print('-----------------------------------')
            print('Распознанный текст:', text[14:-3])
            print('-----------------------------------')
            sound1 = AudioSegment.from_wav(f'audio.wav')
            sound2 = AudioSegment.from_wav(f"звуковая_запись{count}.wav")
            combined_sounds = sound1 + sound2
            combined_sounds.export(f"audio{count}.wav", format="wav")

            if os.path.exists(f"звуковая_запись{count}.wav"):
                os.remove(f"звуковая_запись{count}.wav")
            thread = threading.Thread(target=transcribe, args=(f"audio{count}.wav", ))
            thread.start()
