import logging

from telegram import Update
from telegram.ext import Application, PicklePersistence, CommandHandler, MessageHandler, filters, ContextTypes

from transcribe import TranscribeInterface


class Bot:
    def __init__(self, token):
        builder = Application.builder()
        builder.token(token)
        builder.persistence(PicklePersistence('persistence.pickle'))
        self.logger = logging.getLogger()
        self.services = {}
        self.job_monitor_interval = 10
        self.application = builder.build()
        self.application.add_handler(CommandHandler('start', self.cmd_start))
        self.application.add_handler(MessageHandler(filters.VOICE, self.audio_handler))

    def add_transcribe(self, transcribe: TranscribeInterface):
        self.services[transcribe.get_provider_name()] = transcribe

    def start(self):
        self.application.run_polling()

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sou um bot de transcrição. Qualquer mensagem de áudio enviada a mim ou a um grupo do qual participo"
                 "será transcrita usando serviços de nuvem."
        )

    async def audio_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Recebe uma mensagem de voz e a envia para os serviços de nuvem cadastrados com `self.add_transcribe`
        :param update:
        :param context:
        :return:
        """
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
        for service in self.services.values():
            message = await update.message.reply_text(f"Transcrição no provedor {service.get_provider_name()}\n\n"
                                                      f"Realizando upload")
            url = service.upload(file_cache_path)
            await context.bot.edit_message_text(chat_id=message.chat_id,
                                                message_id=message.id,
                                                text=f"Transcrição no provedor {service.get_provider_name()}\n\n"
                                                     f"Transcrição iniciada")
            result = service.start_transcribe_job(url)
            await context.bot.edit_message_text(chat_id=message.chat_id,
                                                message_id=message.id,
                                                text=f"Transcrição no provedor {service.get_provider_name()}\n\n"
                                                     f"Transcrição concluída:\n\n"
                                                     f"{result}")
