import asyncio
import logging

from transcribe import TranscribeInterface


class Cli:
    def __init__(self, file_path):
        self.logger = logging.getLogger()
        self.services = []
        self.monitor_jobs = []
        self.file = file_path

    def add_transcribe(self, transcribe: TranscribeInterface):
        self.services.append(transcribe)

    def start(self):
        asyncio.run(self.upload_file())

    async def upload_file(self):
        tasks = [
            asyncio.create_task(self.upload_and_start_transcribe(t)) for t in self.services
        ]
        # await asyncio.gather(*tasks)
        for task in tasks:
            await task

    async def upload_and_start_transcribe(self, provider: TranscribeInterface):
        url = await provider.upload(self.file)
        self.logger.info(f"Enviado arquivo para {provider.get_provider_name()}")
        job_id = provider.start_transcribe_job(url)
        await self.start_monitoring_job(provider, job_id)
        
    async def start_monitoring_job(self, provider: TranscribeInterface, job_id: str):
        self.monitor_jobs.append(job_id)
        while job_id in self.monitor_jobs:
            job = await self.callback_monitor(provider, job_id)
            if job is not None:
                self.logger.info(f"Job {job_id} na {provider.get_provider_name()} está {job.status}")
                if job.status == 'COMPLETED':
                    self.logger.info(job.result)

    async def callback_monitor(self, provider: TranscribeInterface, job_id: str):
        job = provider.get_job(job_id)
        if job.status == 'COMPLETED' or job.status == 'FAILED':
            self.monitor_jobs.remove(job_id)
            return job
        else:
            return None
