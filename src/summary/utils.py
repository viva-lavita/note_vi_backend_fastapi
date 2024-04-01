import os
import re
from uuid import UUID
import aiofiles

from fastapi import UploadFile

from src.config import config
from src.constants import get_project_root


def get_dir_path(user_id: UUID, type: str = "other") -> str:
    """
    Возвращает абсолютный путь к файлу(директории).
    """
    return os.path.join(get_project_root(), "static", str(user_id), type)


def get_absolute_file_path(filename: str, user_id: UUID, type: str = "other") -> str:
    """
    Возвращает абсолютный путь к файлу.
    """
    return os.path.join(get_project_root(), "static", str(user_id), type, filename)


def get_file_path(filename: str, user_id: UUID, type: str = "other") -> str:
    """
    Возвращает относительный путь к файлу.

    :param filename: Имя файла
    :param user_id: Идентификатор пользователя
    :param type: Тип файла (модель)
    :return: Относительный путь к файлу
    """
    return os.path.join("static", str(user_id), type, filename)


def secure_filename(filename: str) -> str:
    """
    Проверяет безопасность имени файла.
    Корректирует недопустимые символы.
    """
    # Удаление недопустимых символов
    new_filename = re.sub(r'[^\w\s.-@+]', '', filename)

    # Замена пробелов на подчеркивания
    new_filename = new_filename.replace(' ', '_')

    # Замена / на -
    new_filename = new_filename.replace('/', '-')

    return new_filename


def allowed_file(filename: str) -> bool:
    """Проверяет, является ли формат файла допустимым."""
    return ('.' in filename and filename.rsplit('.', 1)[1].lower()
            in config.ALLOWED_EXTENSIONS)


def allowed_type_summary(filename: str) -> bool:
    """Проверяет, является ли формат конспекта допустимым."""
    return ('.' in filename and filename.rsplit('.', 1)[1].lower()
            in {'md'})


def get_filename(filename: str, user_id: UUID, type: str = "other") -> str:
    """
    Проверяет уникальность имени файла.
    Если имя уже существует, то добавляет к нему цифру.
    """
    counter = 1
    while True:
        if os.path.exists(get_absolute_file_path(filename, user_id, type)):
            _filename = filename.rsplit(".")
            filename = f'{_filename[0]}_{counter}.{_filename[1]}'
            counter += 1
        else:
            break

    return filename


async def save_file(file: UploadFile, filename: str, user_id: UUID, type: str = "other") -> None:
    """
    Сохраняет файл в директорию пользователя.

    :param file: Загруженный файл.
    :param filename: Безопасное имя файла.
    :param user_id: Идентификатор пользователя.
    :param type: Тип файла (модель).
    :return: None

    Создает директорию если ее нет.
    """
    dir_path = get_dir_path(user_id, type)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    async with aiofiles.open(get_absolute_file_path(filename, user_id, type), 'wb') as f:
        await f.write(await file.read())
