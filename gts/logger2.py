import os

LOGGING = {
    # Use v1 of the logging config schema
    'version': 1,
    # Continue to use existing loggers
    'disable_existing_loggers': False,
    # Add a verbose formatter
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    # Create a log handler that prints logs to the terminal
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            # Add the verbose formatter
            'formatter': 'verbose',
        },
        # Add a handler to write logs to a file
        'file': {
            # Use the FileHandler class
            'class': 'logging.handlers.RotatingFileHandler',
            # Specify a local log file as a raw string. Use your app's directory.
            'filename': r'd:/media/log/logs.txt',
            'backupCount': 10,  # keep at most 10 log files
            'maxBytes': 100000,  # 5*1024*1024 bytes (5MB)

        },
    },
    # Define the root logger's settings
    'root': {
        # Use the console and file logger
        'handlers': ['file'],
        'level': 'ERROR',
    },
    # Define the django log module's settings
    'loggers': {
        'django': {
            # Use the console and file logger
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
            'propagate': False,
        },
    },
}
