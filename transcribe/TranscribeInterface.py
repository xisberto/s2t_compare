from pathlib import Path


class TranscribeInterface:

    def get_provider_name(self) -> str:
        pass

    def upload(self, file_path: Path) -> str:
        """
        Uploads a local file to the object storage service
        :param file_path: the local file path
        :return: the object storage file URL
        """
        pass

    def start_transcribe_job(self, file_url: str) -> str:
        """
        Starts a Speech to Text transcribe job on the provider service
        :param file_url: the object storage file URL containing the audio
        :return: the transcribe job id
        """
        pass

    def get_job_status(self, job_id) -> str:
        """
        Gets a Speech to Text transcribe job status
        :param job_id: the job id
        :return: 'QUEUED'|'IN_PROGRESS'|'FAILED'|'COMPLETED'
        """
        pass
