import os
import uuid
from pydub import AudioSegment
from gateway.audio.diarize import diarizer
from gateway.audio.transcriber import run
import os


def processing(test_audio, voice):
    combined_filename = f'audio-temp/{uuid.uuid4()}.wav'
    cmd = f"ffmpeg -i {test_audio} -i {voice} -filter_complex concat=n=2:v=0:a=1 {combined_filename}"
    os.system(cmd)
    professor = diarizer(combined_filename)
    transcription = None
    if professor:
        fixed_filename = f'audio-temp/{uuid.uuid4()}.wav'
        quite = f'{os.getcwd()}/gateway/audio/audio_files/quite.wav'
        cmd = f"ffmpeg -i {quite} -i {voice} -filter_complex concat=n=2:v=0:a=1 {fixed_filename}"
        os.system(cmd)
        transcription = run(fixed_filename)
        if os.path.exists(fixed_filename):
            os.remove(fixed_filename)
    if os.path.exists(combined_filename):
        os.remove(combined_filename)
    return transcription
