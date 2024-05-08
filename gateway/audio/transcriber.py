import grpc

import yandex.cloud.ai.stt.v3.stt_pb2 as stt_pb2
import yandex.cloud.ai.stt.v3.stt_service_pb2_grpc as stt_service_pb2_grpc

CHUNK_SIZE = 16000
API_KEY = 'AQVNyxAphUPg01f3J9GljwCDRPeetoSvD6XhERD1'


def gen(audio_file_name):
    recognize_options = stt_pb2.StreamingOptions(
        recognition_model=stt_pb2.RecognitionModelOptions(
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
    with open(audio_file_name, 'rb') as f:
        data = f.read(CHUNK_SIZE)
        while data != b'':
            yield stt_pb2.StreamingRequest(chunk=stt_pb2.AudioChunk(data=data))
            data = f.read(CHUNK_SIZE)


def run(audio_file_name):
    # Установите соединение с сервером.
    cred = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
    stub = stt_service_pb2_grpc.RecognizerStub(channel)

    # Отправьте данные для распознавания.
    it = stub.RecognizeStreaming(gen(audio_file_name), metadata=(
       ('authorization', f'Api-Key {API_KEY}'),
    ))

    data = []
    try:
        for r in it:
            event_type, alternatives = r.WhichOneof('Event'), None
            if event_type == 'final_refinement':
                alternatives = [a.text for a in r.final_refinement.normalized_text.alternatives]
                data.extend(alternatives)
        return '. '.join(set(data))
    except grpc._channel._Rendezvous as err:
        print(f'Error code {err._state.code}, message: {err._state.details}')
        raise err


# print(run(r'C:\Users\Lenovo\PycharmProjects\Examoff\gateway\audio\audio_files\audio_old.wav'))
