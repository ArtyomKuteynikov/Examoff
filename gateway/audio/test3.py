import argparse
import speech_recognition as sr
from pydub import AudioSegment


def recognize_speech(audio_file, intervals):
    recognizer = sr.Recognizer()

    audio = AudioSegment.from_wav(audio_file)

    for interval in intervals:
        start_time, end_time = interval
        start_frame = int(start_time * 1000)  # переводим в миллисекунды
        end_frame = int(end_time * 1000)  # переводим в миллисекунды
        segment = audio[start_frame:end_frame]

        with sr.AudioFile(segment.export(format='wav')) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            print(f"Распознанный текст для интервала {interval}: {text}")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio', required=True, help='путь к аудиофайлу')
    args = parser.parse_args()

    intervals = [(0, 7.68251273344652), (7.68251273344652, 13.33616298811545)]

    recognize_speech(args.audio, intervals)
