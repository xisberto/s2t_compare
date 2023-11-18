import logging


class TranscribeInterface:

    async def upload(self, file_path: str) -> str:
        """
        Uploads a local file to the object storage service
        :param file_path: the local file path
        :return: the object storage file URL
        """
        pass

    async def transcribe(self, file_url: str) -> str:
        """
        Starts a Speech to Text transcribe job on the provider service
        :param file_url: the object storage file URL containing the audio
        :return: ???
        """
        pass
