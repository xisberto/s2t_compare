import logging
import os

from dotenv import dotenv_values

import aws
from bot import Bot

if __name__ == '__main__':
    config = {
        **dotenv_values(".env"),
        **os.environ
    }
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    aws_transcribe = aws.Transcribe(config['AWS_BUCKET'])
    bot = Bot(config['TOKEN'])
    bot.add_transcribe(aws_transcribe)
    bot.start()
