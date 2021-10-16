ERROR_LOG_FILENAME = 'data/log_error.log'

logger_config = {
    'version': 1,
    'disable_existing_loggers': False,  # Отключаем все логеры, которые здесь не упомянуты

    'formatters': {
        'std_format': {
            'format': '{asctime} [{name}] {levelname}: {module}:{funcName}:{lineno}:{message}',
            'datefmt': '%d.%m.%Y %H:%M:%S',
            'style': '{'
        },
        'console_format': {
            'format': '{asctime} [{name}] {levelname}: {message}',
            'datefmt': '%d.%m.%Y %H:%M:%S',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'console_format'
        },
        "logfile": {  # The handler name
                    'formatter': 'std_format',  # Refer to the formatter defined above
                    'level': 'ERROR',  # FILTER: Only ERROR and CRITICAL logs
                    'class': 'logging.handlers.RotatingFileHandler',  # OUTPUT: Which class to use
                    'filename': ERROR_LOG_FILENAME,  # Param for class above. Defines filename to use, load it from constant

                },
    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'logfile']
            #'propagate': False
        },
    },

}