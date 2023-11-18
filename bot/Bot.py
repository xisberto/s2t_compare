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
        self.services = []
        self.job_monitor_interval = 10
        self.application = builder.build()
        self.application.add_handler(CommandHandler('start', self.cmd_start))
        self.application.add_handler(MessageHandler(filters.VOICE, self.audio_handler))

    def add_transcribe(self, transcribe: TranscribeInterface):
        self.services.append(transcribe)

    def start(self):
        self.application.run_polling()

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sou um bot de transcrição. Qualquer mensagem de áudio enviada a mim ou a um grupo do qual participo"
                 "será transcrita usando serviços de nuvem."
        )

    async def audio_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            url = transcribe.upload(file_cache_path)
            self.logger.info(f"Uploaded to {url}")
            job_id = transcribe.start_transcribe_job(url)
            await self.start_monitoring_job(transcribe, job_id, update.effective_chat.id)

    async def start_monitoring_job(self, provider: TranscribeInterface, job_id: str, chat_id: int):
        chat_data = await self.application.persistence.get_chat_data()
        provider_name = provider.get_provider_name()
        if provider_name not in chat_data:
            chat_data[provider_name] = [job_id]
        else:
            chat_data[provider_name].append(job_id)
        await self.application.persistence.update_chat_data(chat_id, chat_data)
        self.application.job_queue.run_repeating(
            callback=self.callback_monitor,
            interval=self.job_monitor_interval,
            first=0,
            name=job_id,
            chat_id=chat_id,
            data=provider_name
        )

    async def callback_monitor(self, context: ContextTypes.DEFAULT_TYPE):
        provider_name = context.job.data
        job_id = context.job.name
        self.logger.info(f"Getting status for {job_id} on {provider_name}")
        provider = [p for p in self.services if p.get_provider_name() == provider_name][0]
        status = provider.get_job_status(job_id)
        self.logger.info(f"{job_id} on {provider_name} status: {status}")
        if status == 'COMPLETED':
            await context.bot.send_message(context.job.chat_id, f"Transcrição na {provider_name} concluída.")
            # TODO get job result
            context.job.schedule_removal()
        elif status == 'FAILED':
            await context.bot.send_message(context.job.chat_id, f"Transcrição na {provider_name} falhou.")
            context.job.schedule_removal()
        else:
            await context.bot.send_message(context.job.chat_id, f"Transcrição na {provider_name} ainda executando.")
