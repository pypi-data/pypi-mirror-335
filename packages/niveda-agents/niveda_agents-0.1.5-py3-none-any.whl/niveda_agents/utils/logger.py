import os
import logging


def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('niveda_agents')
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        logger.handlers.clear()

    log_file = 'logs/logs.txt'
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
