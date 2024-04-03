class FilesNotFoundError(Exception):
    status_code = 404
    description = "Файлы не найдены"


class SummaryNotFoundError(Exception):
    status_code = 404
    description = "Конспекты не найдены"


class ImageNotFoundError(Exception):
    status_code = 404
    description = "Изображения не найдены"