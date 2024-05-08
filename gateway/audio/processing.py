import os
import uuid
from pydub import AudioSegment
from gateway.audio.diarize import diarizer
from gateway.audio.transcriber import run


def processing(test_audio, voice):
    sound1 = AudioSegment.from_wav(test_audio)
    sound2 = AudioSegment.from_wav(voice)
    combined_sounds = sound1 + sound2
    combined_filename = f'audio-temp/{uuid.uuid4()}.wav'
    combined_sounds.export(combined_filename, format="wav")
    professor = diarizer(combined_filename)
    transcription = None
    if professor:
        transcription = run(voice)
    if os.path.exists(combined_filename):
        os.remove(combined_filename)
    return transcription


import time
t1 = time.time()
print(processing(r'C:\Users\Lenovo\PycharmProjects\Examoff\gateway\audio\audio_files\audio2.wav', r'C:\Users\Lenovo\PycharmProjects\Examoff\gateway\audio\audio_files\audio.wav'))
print(time.time() - t1)
