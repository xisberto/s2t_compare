import logging
import pathlib

import boto3


class Transcribe:
    def __init__(self, bucket_name):
        self.logger = logging.getLogger()
        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(bucket_name)

    def upload(self, file_path: str):
        self.logger.info(f"Uploading {file_path}")
        with open(file_path, 'rb') as data:
            self.bucket.put_object(Key=file_path, Body=data)
