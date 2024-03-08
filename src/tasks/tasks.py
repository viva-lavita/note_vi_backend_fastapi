import smtplib
from email.message import EmailMessage

from celery import Celery

from src.config import config
from src.tasks.templates import (
    get_email_template_verify, get_email_template_register
)


celery = Celery(
    'tasks',
    broker=config.REDIS_URL,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    backend=config.REDIS_URL + '/0'
)


@celery.task
def send_email_register(username: str, user_email: str) -> None:
    """
    Отправка письма с подтверждением регистрации.
    """
    email = get_email_template_register(username, user_email)
    with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT) as server:
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(email)


@celery.task
def send_email_verify(username: str, user_email: str, token: str) -> None:
    """
    Отправка письма с подтверждением верификации.
    """
    email = get_email_template_verify(username, user_email, token)
    with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT) as server:
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(email)
