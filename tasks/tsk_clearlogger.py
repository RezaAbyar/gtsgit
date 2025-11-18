import logging

def clear_logs():
    log_file_path = 'd:/media/log/logs.txt'
    with open(log_file_path, 'w'):
        pass  # فایل لاگ را خالی می‌کند
    logging.info('Log file cleared.')
