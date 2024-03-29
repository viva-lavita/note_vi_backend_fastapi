from src.config import config


LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'src.logs.json_logger.JSONLogFormatter',
        },
        'default': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        }
    },
    'handlers': {
        # Используем AsyncLogDispatcher для асинхронного вывода потока.
        'json': {
            'formatter': 'json',
            'class': 'asynclog.AsyncLogDispatcher',
            'func': 'src.logs.json_logger.write_log',
        },
        'console': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'root': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'INFO' if config.API_DEBUG else 'WARNING',
            'propagate': False,
        },
        'tests': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'INFO',
            'propagate': False,
        },
        'uvicorn': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'INFO' if config.API_DEBUG else 'WARNING',
            'propagate': False,
            'qualname': 'uvicorn',
        },
        # Не даем стандартному логгеру fastapi работать по пустякам и замедлять работу сервиса
        'uvicorn.access': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'ERROR',
            'propagate': False,
        },
        'uvicorn.error': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'WARNING',
            'propagate': False,
        },
        'celerybeat': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'WARNING',
            'propagate': False,
        },
        'postgresql': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'WARNING',
            'propagate': False,
            'qualname': 'postgresql',
        },
        'sqlalchemy': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'WARNING',
            'propagate': False,
        },
        'redis': {
            'handlers': ['json', 'console'] if config.API_DEBUG else ['json'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
