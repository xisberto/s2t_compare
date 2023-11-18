import logging
import os

from dotenv import dotenv_values
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
    Bot(config['TOKEN'], config['AWS_BUCKET']).start()
