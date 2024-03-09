#!/bin/bash



if [[ "${1}" == "celery" ]]; then
  mkdir logs
  cd logs
  touch celery.log
  cd ..
  celery --app=src.tasks.tasks:celery worker -l INFO --logfile=/note_vi_backend/logs/celery.log
elif [[ "${1}" == "flower" ]]; then
  celery --app=src.tasks.tasks:celery flower
 fi