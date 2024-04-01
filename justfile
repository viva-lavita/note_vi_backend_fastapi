run:
  uvicorn src.main:app --reload

up:
  docker-compose up -d

kill:
  docker-compose kill

build:
  docker-compose build

ps:
  docker-compose ps

exec *args:
  docker-compose exec app {{args}}

logs *args:
  docker-compose logs {{args}} -f

mm *args:
  docker compose exec app alembic revision --autogenerate -m "{{args}}"

migrate:
  docker compose exec app alembic upgrade head

downgrade *args:
  docker compose exec app alembic downgrade {{args}}

ruff *args:
  docker compose exec app ruff {{args}} src
  docker compose exec app ruff format src

lint:
  just ruff --fix

backup:
  docker compose exec app_db scripts/backup

mount-docker-backup *args:
  docker cp app_db:/backups/{{args}} ./{{args}}

restore *args:
    docker compose exec app_db scripts/restore {{args}}

test *args:
    docker compose exec app pytest {{args}}

create network:
    docker network create app_main

tests:
    docker compose exec app pytest

locmigrate:
    alembic upgrade head

bd *args:
    alembic revision --autogenerate -m "{{args}}"
