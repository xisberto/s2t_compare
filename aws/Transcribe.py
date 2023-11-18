import logging
import os
import re
from pathlib import Path

import boto3

from transcribe import TranscribeInterface


class Transcribe(TranscribeInterface):
    def __init__(self, bucket_name):
        self.logger = logging.getLogger()
        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(bucket_name)
        self.client = boto3.client('transcribe')

    def upload(self, file_path: Path) -> str:
        self.logger.info(f"Uploading {file_path}")
        with open(file_path, 'rb') as data:
            self.bucket.put_object(Key=file_path.name, Body=data)
        return f'https://{self.bucket.name}.s3.{os.getenv("AWS_DEFAULT_REGION")}.amazonaws.com/{file_path.name}'

    def start_transcribe_job(self, file_url: str) -> str:
        job_name = re.findall(r"([a-zA-Z0-9_-]+).(oga)", file_url)[0][0]
        self.logger.info(f"Starting Transcription for {job_name}")
        self.client.start_transcription_job(
            TranscriptionJobName=job_name,
            MediaFormat='ogg',
            LanguageCode="pt-BR",
            Media={'MediaFileUri': file_url}
        )
        return job_name

    def get_job_status(self, job_id) -> str:
        job = self.client.get_transcription_job(TranscriptionJobName=job_id)
        return job['TranscriptionJob']['TranscriptionJobStatus']
