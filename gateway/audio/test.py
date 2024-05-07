# coding=utf8
import argparse
import subprocess

import grpc
from pydub import AudioSegment

import yandex.cloud.ai.stt.v3.stt_pb2 as stt_pb2
import yandex.cloud.ai.stt.v3.stt_service_pb2_grpc as stt_service_pb2_grpc

CHUNK_SIZE = 4000


def convert_wavfile(wavfile, outfile):
    """
    Converts file to 16khz single channel mono wav
    """
    cmd = r"ffmpeg -y -i {} -acodec pcm_s16le -ar 16000 -ac 1 {}".format(
        wavfile, outfile
    )
    subprocess.Popen(cmd, shell=True).wait()
    return outfile


def gen(audio_file_name):
    # Задайте настройки распознавания.

    audio = AudioSegment.from_wav(audio_file_name)
    start_frame = int(7.68251273344652 * 1000)  # переводим в миллисекунды
    end_frame = int(13.33616298811545 * 1000)  # переводим в миллисекунды
    audio = audio[start_frame:end_frame]
    recognize_options = stt_pb2.StreamingOptions(
        speaker_labeling=stt_pb2.SpeakerLabelingOptions(
            # Enable speaker labeling
            speaker_labeling=stt_pb2.SpeakerLabelingOptions.SPEAKER_LABELING_ENABLED
        ),
        recognition_model=stt_pb2.RecognitionModelOptions(
            model="general:rc",
            audio_format=stt_pb2.AudioFormatOptions(
                container_audio=stt_pb2.ContainerAudio(
                    container_audio_type=stt_pb2.ContainerAudio.WAV
                )
            ),
            text_normalization=stt_pb2.TextNormalizationOptions(
                text_normalization=stt_pb2.TextNormalizationOptions.TEXT_NORMALIZATION_ENABLED,
                profanity_filter=True,
                literature_text=False
            ),
            language_restriction=stt_pb2.LanguageRestrictionOptions(
                restriction_type=stt_pb2.LanguageRestrictionOptions.WHITELIST,
                language_code=['ru-RU']
            ),
            audio_processing_type=stt_pb2.RecognitionModelOptions.FULL_DATA
        )
    )
    # Отправьте сообщение с настройками распознавания.
    yield stt_pb2.StreamingRequest(session_options=recognize_options)

    # Прочитайте аудиофайл и отправьте его содержимое порциями.
    chunk_size = 16000
    audio_data = audio.raw_data
    for i in range(0, len(audio_data), chunk_size):
        yield stt_pb2.StreamingRequest(chunk=stt_pb2.AudioChunk(data=audio_data[i:i + chunk_size]))


def run(audio_file_name):
    # Установите соединение с сервером.
    cred = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
    stub = stt_service_pb2_grpc.RecognizerStub(channel)
    audio_file_name = convert_wavfile(audio_file_name, 'audio_converted.wav')

    # Отправьте данные для распознавания.
    it = stub.RecognizeStreaming(gen(audio_file_name), metadata=(
        # Параметры для авторизации с IAM-токеном
        ('authorization', f'Api-Key AQVNyxAphUPg01f3J9GljwCDRPeetoSvD6XhERD1'),
    ))
    try:
        speaker_label = None
        for r in it:
            event_type, alternatives = r.WhichOneof('Event'), None
            if event_type == 'final_refinement':
                alternatives = [a.text for a in r.final_refinement.normalized_text.alternatives]
                print(f'type={event_type}, alternatives={alternatives}, channel_tag = {r.channel_tag}')
    except grpc._channel._Rendezvous as err:
        print(f'Error code {err._state.code}, message: {err._state.details}')
        raise err


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='audio file path')
    args = parser.parse_args()
    run(args.path)
