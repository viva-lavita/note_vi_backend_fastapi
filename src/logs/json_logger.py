import datetime
import json
import logging
import traceback

from src.config import config
from src.logs.schemas import BaseJsonLogSchema


class JSONLogFormatter(logging.Formatter):
    """
    Кастомизированный класс-форматер для логов в формате json.
    """

    def format(self, record: logging.LogRecord, *args, **kwargs) -> str:
        """
        Преобразование объект журнала в json.

        :param record: объект журнала
        :return: строка журнала в JSON формате
        """
        log_object = self._format_log_object(record)
        return json.dumps(log_object, ensure_ascii=False)

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> dict:
        """
        Перевод записи объекта журнала
        в json формат с необходимым перечнем полей.

        :param record: объект журнала
        :return: Словарь с объектами журнала
        """
        now = datetime \
            .datetime \
            .fromtimestamp(record.created) \
            .astimezone() \
            .replace(microsecond=0) \
            .isoformat()
        message = record.getMessage()
        duration = record.duration \
            if hasattr(record, 'duration') \
            else record.msecs
        # Инициализация тела журнала
        json_log_fields = BaseJsonLogSchema(
            thread=record.process,
            timestamp=now,
            level=record.levelno,
            level_name=config.LOGGER_CONSOLE_LEVEL,
            message=message,
            source=record.name,
            duration=duration,
            app_name=config.PROJECT_NAME,
            app_version=config.APP_VERSION,
            app_env=config.ENVIRONMENT,
        )

        if hasattr(record, 'props'):
            json_log_fields.props = record.props

        if record.exc_info:
            json_log_fields.exceptions = \
                traceback.format_exception(*record.exc_info)

        elif record.exc_text:
            json_log_fields.exceptions = record.exc_text
        # Преобразование Pydantic объекта в словарь
        json_log_object = json_log_fields.dict(
            exclude_unset=True,
            by_alias=True,
        )
        # Соединение дополнительных полей логирования
        if hasattr(record, 'request_json_fields'):
            json_log_object.update(record.request_json_fields)

        return json_log_object


def write_log(msg):
    """
    Куда выводим/отправляем логи.

    Тут можно прописать, куда выводим файл.
    Сейчас логи пишем в один файл в директории logs.
    """
    with open('logs/logs.json', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
