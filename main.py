import logging
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from dotenv import dotenv_values

import aws
from bot import Bot
from cli import Cli

if __name__ == '__main__':
    config = {
        **dotenv_values(".env"),
        **os.environ
    }
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    arg_parser = ArgumentParser()
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file")
    group.add_argument("-b", "--bot", action="store_true")
    args = arg_parser.parse_args()
    print(args)

    aws_transcribe = aws.Transcribe(config['AWS_BUCKET'])
    # google
    # azure
    if args.bot:
        bot = Bot(config['TOKEN'])
        bot.add_transcribe(aws_transcribe)
        bot.start()
    else:
        file_path = Path(args.file)
        if not file_path.is_file():
            print("O arquivo informado não é válido", file=sys.stderr)
            raise SystemExit(1)
        cli = Cli(file_path)
        cli.add_transcribe(aws_transcribe)
        cli.start()
