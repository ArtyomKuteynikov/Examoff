# 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
import torchaudio
from pyannote.audio import Pipeline
import speech_recognition as sr
from pydub import AudioSegment

torchaudio.set_audio_backend("soundfile")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="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")


def recognize_speech(audio_file, intervals):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(audio_file)
    question = ''
    for interval in intervals:
        start_time, end_time = interval
        start_frame = int(start_time * 1000) - 500  # переводим в миллисекунды
        end_frame = min(int(end_time * 1000) + 500, len(audio))  # переводим в миллисекунды
        segment = audio[start_frame:end_frame]
        with sr.AudioFile(segment.export(format='wav')) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            question += text
        except Exception:
            pass
    return question


def transcribe(file):
    diarization = pipeline(file)
    diarizated = [[turn, speaker] for turn, _, speaker in diarization.itertracks(yield_label=True)]
    student = diarizated[0][1]
    speaker = diarizated[-1][1]
    if speaker == student:
        print('-----------------------------------')
        print('Сказал студент')
        print('-----------------------------------')
    else:
        print('-----------------------------------')
        print('Сказал преподаватель')
        print('-----------------------------------')
    # print(student, speaker)
    # for turn, speaker in diarizated:
    #     if speaker == student:
    #         print('-----------------------------------')
    #         print('Сказал преподаватель')
    #         print('-----------------------------------')
    #     else:
    #         print('-----------------------------------')
    #         print('Сказал студент')
    #         print('-----------------------------------')
    # if speaker in prepod:
    #    prepod[speaker].append([turn.start, turn.end])
    # else:
    #    prepod.update({speaker: [[turn.start, turn.end]]})
    # print(prepod)
    # for i in prepod:
    #     print('speaker: ', i, 'сказал -', recognize_speech(file, prepod[i]))
