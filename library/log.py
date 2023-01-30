# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 16:03
# @Brief   : 日志设置
# ===============================================================

import logging
import os

LOG_CONFIG = {
    'format': '%(asctime)s %(levelname)s [%(filename)s %(funcName)s line:%(lineno)d]: %(message)s',
    'level': int(os.getenv('LOG_LEVEL', logging.INFO)),
    'datefmt': None,
}


class Log(object):
    """
        Log Wrapper. Usage:
        >>> logger = Log(filename='app.log').get_logger()
        >>> logger.warn('This is warning')
        >>> logger.info('This is info')
    """
    def __init__(self, log_config: dict=None):
        if log_config is None:
            log_config = LOG_CONFIG
        logging.basicConfig(**log_config)

    @staticmethod
    def get_logger(log_name=None):
        logger = logging.getLogger(log_name)
        return logger
