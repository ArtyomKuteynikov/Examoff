# 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
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="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")


def diarizer(file):
    diarization = pipeline(file)
    diarizated = [[turn, speaker] for turn, _, speaker in diarization.itertracks(yield_label=True)]
    student = diarizated[0][1]
    speaker = diarizated[-1][1]
    if speaker == student:
        print('-----------------------------------')
        print('Сказал студент')
        print('-----------------------------------')
        return False
    else:
        print('-----------------------------------')
        print('Сказал преподаватель')
        print('-----------------------------------')
        return True
