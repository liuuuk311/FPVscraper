from celery.utils.log import get_task_logger

from helpers.telegram import telegram_log

celery_logger = get_task_logger(__name__)


class LoggerAdapter:
    def __init__(self, l):
        self._logger = l

    def info(self, message, send_to_telegram=False):
        self._logger.info(message)

        if send_to_telegram:
            telegram_log(message)


logger = LoggerAdapter(celery_logger)
