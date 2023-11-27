import logging

from telegram import Update
from telegram.ext import Application, PicklePersistence, CommandHandler, MessageHandler, filters, ContextTypes, Job

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
        for transcribe in self.services.values():
            url = await transcribe.upload(file_cache_path)
            self.logger.info(f"Uploaded to {url}")
            job_id = transcribe.start_transcribe_job(url)
            await self.start_monitoring_job(transcribe, job_id, update.effective_chat.id)

    async def start_monitoring_job(self, provider: TranscribeInterface, job_id: str, chat_id: int):
        """
        Adiciona um job ao application.job_queue para verificar o andamento do job
        :param provider:
        :param job_id:
        :param chat_id:
        :return:
        """
        # chat_data[provider_name] é uma lista contendo os jobs em andamento para aquele chat
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
            first=1,
            name=job_id,
            chat_id=chat_id,
            data=provider_name
        )

    async def callback_monitor(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Verifica o andamento de um job e retorna o resultado. Deve ser chamado usando job_queue.
        O parâmetro data deve ser alimentado com o nome do provedor de nuvem (chave de chat_id).
        :param context:
        :return:
        """
        provider_name = context.job.data
        job_id = context.job.name
        self.logger.info(f"Getting status for {job_id} on {provider_name}")
        provider = self.services[provider_name]
        job = provider.get_job(job_id)
        self.logger.info(f"{job_id} on {provider_name} status: {job.status}")
        if job.status == 'COMPLETED':
            await self.clear_job(context)
            await context.bot.send_message(context.job.chat_id, f"Transcrição na {provider_name} concluída.\n\n"
                                                                f"{job.result}")
        elif job.status == 'FAILED':
            await self.clear_job(context)
            await context.bot.send_message(context.job.chat_id, f"Transcrição na {provider_name} falhou.")
        else:
            await context.bot.send_message(context.job.chat_id, f"Transcrição na {provider_name} ainda executando.")

    async def clear_job(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Limpa os dados de um job.
        Remove a informação daquele job de chat_data.
        Remove o job da job_queue
        :param context:
        :return:
        """
        job_id = context.job.name
        provider_name = context.job.data
        chat_data = context.chat_data
        chat_data[provider_name].remove(job_id)
        await self.application.persistence.update_chat_data(context.job.chat_id, chat_data)
        context.job.schedule_removal()
