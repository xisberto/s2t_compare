import logging

from telegram import Update
from telegram.ext import Application, PicklePersistence, CommandHandler, MessageHandler, filters, \
    CallbackContext

from transcribe import TranscribeInterface


class Bot:
    def __init__(self, token):
        builder = Application.builder()
        builder.token(token)
        builder.persistence(PicklePersistence('persistence.pickle'))
        self.logger = logging.getLogger()
        self.services = []
        self.application = builder.build()
        self.application.add_handler(CommandHandler('start', self.cmd_start))
        self.application.add_handler(MessageHandler(filters.VOICE, self.audio_handler))

    def add_transcribe(self, transcribe: TranscribeInterface):
        self.services.append(transcribe)

    def start(self):
        self.application.run_polling()

    async def cmd_start(self, update: Update, context: CallbackContext):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sou um bot de transcrição. Qualquer mensagem de áudio enviada a mim ou a um grupo do qual participo"
                 "será transcrita usando serviços de nuvem."
        )

    async def audio_handler(self, update: Update, context: CallbackContext):
        self.logger.info("Recebi uma mensagem de voz")
        voice = update.message.voice
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Mensagem de voz com {voice.duration} segundos e {voice.file_size} bytes."
        )
        file = await voice.get_file()
        self.logger.info(file.file_path)
        self.logger.info(file.file_id)
        file_cache_path = await file.download_to_drive(custom_path=f"cache/{file.file_id}.oga")
        for transcribe in self.services:
            transcribe.upload(f"cache/{file_cache_path.name}")
