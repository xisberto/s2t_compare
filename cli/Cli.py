import logging
from typing import List

from transcribe import TranscribeInterface


class Cli:
    def __init__(self, file_path):
        self.logger = logging.getLogger()
        self.services: List[TranscribeInterface] = []
        self.monitor_jobs = []
        self.file = file_path

    def add_transcribe(self, transcribe: TranscribeInterface):
        self.services.append(transcribe)

    def start(self):
        result = []
        for service in self.services:
            result.append({
                'result': self.upload_and_start_transcribe(service),
                'provider': service.get_provider_name()
            })
        return result

    def upload_and_start_transcribe(self, provider: TranscribeInterface):
        url = provider.upload(self.file)
        self.logger.info(f"Enviado arquivo para {provider.get_provider_name()}")
        return provider.start_transcribe_job(url)

    def start_monitoring_job(self, provider: TranscribeInterface, job_id: str):
        self.monitor_jobs.append(job_id)
        while job_id in self.monitor_jobs:
            job = self.callback_monitor(provider, job_id)
            if job is not None:
                self.logger.info(f"Job {job_id} na {provider.get_provider_name()} está {job.status}")
                if job.status == 'COMPLETED':
                    self.logger.info(job.result)

    def callback_monitor(self, provider: TranscribeInterface, job_id: str):
        job = provider.get_job(job_id)
        if job is not None and (job.status == 'COMPLETED' or job.status == 'FAILED'):
            self.monitor_jobs.remove(job_id)
            return job
        else:
            return None
