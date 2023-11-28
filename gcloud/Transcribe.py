from google.cloud import speech
import os

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./ppgia-405916-05b747e7f98d.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./ppgia-405916-a846a23e57a9.json"

def transcribe_gcs(gcs_uri: str) -> str:
    """Asynchronously transcribes the audio file specified by the gcs_uri.

    Args:
        gcs_uri: The Google Cloud Storage path to an audio file.

    Returns:
        The generated transcript from the audio file provided.
    """

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        # sample_rate_hertz=44100,
        language_code="pt_BR",
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    transcript_builder = []
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
        transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")

    transcript = "".join(transcript_builder)
    print(transcript)

    return transcript

def speech_to_text(
    config: speech.RecognitionConfig,
    audio: speech.RecognitionAudio,
) -> speech.RecognizeResponse:
    client = speech.SpeechClient()

    # Synchronous speech recognition request
    response = client.recognize(config=config, audio=audio)

    return response


def print_response(response: speech.RecognizeResponse):
    for result in response.results:
        print_result(result)


def print_result(result: speech.SpeechRecognitionResult):
    best_alternative = result.alternatives[0]
    print("-" * 80)
    print(f"language_code: {result.language_code}")
    print(f"transcript:    {best_alternative.transcript}")
    print(f"confidence:    {best_alternative.confidence:.0%}")

if __name__ == '__main__':
    config = speech.RecognitionConfig(
        language_code="pt_BR",
    )
    audio = speech.RecognitionAudio(
        # uri="gs://cloud-samples-data/speech/brooklyn_bridge.flac",
        # uri="gs://ppgia-bucket/audio-files/transcribe.mp3"
        # uri="gs://ppgia-bucket/audio-files/transcribe.ogg"
        uri="gs://ppgia-bucket/audio-files/transcribe.wav"
    )

    response = speech_to_text(config, audio)
    print_response(response)