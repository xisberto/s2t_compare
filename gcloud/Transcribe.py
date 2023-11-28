from pathlib import Path

from google.cloud import speech
from google.cloud import storage
import os

from google.longrunning.operations_pb2 import GetOperationRequest

from transcribe import TranscribeInterface, Job

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./authentication.json"


class Transcribe(TranscribeInterface):
    def __init__(self, bucket_name):
        self.client = speech.SpeechClient()
        gcs = storage.Client()
        self.bucket = gcs.get_bucket(bucket_name)

    def get_provider_name(self) -> str:
        return "Google"

    async def upload(self, file_path: Path) -> str:
        # blob = self.bucket.blob(file_path.name)
        # precondition = 0
        # blob.upload_from_filename(file_path.absolute(), if_generation_match=precondition)
        return f'gs://ppgia-bucket/{file_path.name}'

    def start_transcribe_job(self, file_url: str) -> str:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="pt_BR",
        )
        audio = speech.RecognitionAudio(
            uri=file_url
        )

        response = self.speech_to_text(config, audio)
        return response

    # def get_job(self, job_id) -> Job:
    #     return Job(job_id, 'COMPLETED', self.transcript)
    def get_job(self, job_id) -> Job:
        request = GetOperationRequest(name=job_id)
        operation = self.client.get_operation(request)
        print(operation)

    def speech_to_text(self,
        config: speech.RecognitionConfig,
        audio: speech.RecognitionAudio,
    ) -> speech.RecognizeResponse:
        client = speech.SpeechClient()

        # Synchronous speech recognition request
        # response = client.recognize(config=config, audio=audio)
        # self.transcript = response
        # return response

        operation = client.long_running_recognize(config=config, audio=audio)
        # response = operation.result(timeout=90)
        # transcript_builder = []
        # # Each result is for a consecutive portion of the audio. Iterate through
        # # them to get the transcripts for the entire audio file.
        # for result in response.results:
        #     # The first alternative is the most likely one for this portion.
        #     transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
        #     transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")
        #
        # transcript = "".join(transcript_builder)
        #
        # return transcript
        return operation.operation.request_id


#
# def transcribe_gcs(gcs_uri: str) -> str:
#     """Asynchronously transcribes the audio file specified by the gcs_uri.
#
#     Args:
#         gcs_uri: The Google Cloud Storage path to an audio file.
#
#     Returns:
#         The generated transcript from the audio file provided.
#     """
#
#     client = speech.SpeechClient()
#
#     audio = speech.RecognitionAudio(uri=gcs_uri)
#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
#         # sample_rate_hertz=44100,
#         language_code="pt_BR",
#     )
#
#     operation = client.long_running_recognize(config=config, audio=audio)
#
#     print("Waiting for operation to complete...")
#     response = operation.result(timeout=90)
#
#     transcript_builder = []
#     # Each result is for a consecutive portion of the audio. Iterate through
#     # them to get the transcripts for the entire audio file.
#     for result in response.results:
#         # The first alternative is the most likely one for this portion.
#         transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
#         transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")
#
#     transcript = "".join(transcript_builder)
#     print(transcript)
#
#     return transcript
#
# def speech_to_text(
#     config: speech.RecognitionConfig,
#     audio: speech.RecognitionAudio,
# ) -> speech.RecognizeResponse:
#     client = speech.SpeechClient()
#
#     # Synchronous speech recognition request
#     response = client.recognize(config=config, audio=audio)
#     alternative_transcript = ''
#     for result in response.results:
#         best_alternative = result.alternatives[0]
#         alternative_transcript = best_alternative.transcript
#
#     return alternative_transcript
#
#
# def print_response(response: speech.RecognizeResponse):
#     for result in response.results:
#         print_result(result)
#
#
# def print_result(result: speech.SpeechRecognitionResult):
#     best_alternative = result.alternatives[0]
#     print("-" * 80)
#     print(f"language_code: {result.language_code}")
#     print(f"transcript:    {best_alternative.transcript}")
#     print(f"confidence:    {best_alternative.confidence:.0%}")
#
# if __name__ == '__main__':
#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
#         sample_rate_hertz=48000,
#         language_code="pt_BR",
#     )
#     audio = speech.RecognitionAudio(
#         # uri="gs://ppgia-bucket/audio-files/transcribe.wav"
#         uri="gs://ppgia-bucket/voice.ogx"
#     )
#
#     response = speech_to_text(config, audio)
#     print_response(response)
#
#     # transcribe = Transcribe('ppgia-bucket')
#     # transcribe.upload(Path('./voice.ogx'))