# Шаг #1 | Установка зависимостей
FROM python:3.12-slim-bullseye as build-image

RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/cache/apt/*

# Установка переменных окружения
ENV APP_ROOT /src
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH "${PYTHONPATH}:${APP_ROOT}"
ENV APP_USER service_user

# Создание пользователя и установка прав доступа
RUN groupadd -r docker \
    && useradd -m --home-dir ${APP_ROOT} -s /usr/sbin/nologin -g docker ${APP_USER} \
    && usermod -aG sudo ${APP_USER}

# Шаг #2 | Установка Poetry
FROM build-image as poetry-init
ARG APP_ROOT
WORKDIR ${APP_ROOT}
RUN pip install --no-cache-dir poetry==1.5.1 \
    && poetry config virtualenvs.create false

# Шаг #3 | Установка зависимостей проекта
FROM poetry-init as poetry-install
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction --no-ansi

# Шаг #4 | Финальная настройка и запуск приложения
FROM poetry-install as run-app
COPY . .
ENV PATH "$PATH:/src/scripts"

RUN useradd -m -d /src -s /bin/bash app \
    && chown -R app:app /src/* && chmod +x /src/scripts/*

WORKDIR ${APP_ROOT}
USER app
CMD ["./scripts/start-dev.sh"]