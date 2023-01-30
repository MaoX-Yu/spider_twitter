# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 15:48
# @Brief   : 初始化redis连接
# ===============================================================

import threading

from retrying import retry

from library import config
from library.log import Log
from library.initializer.redis_client import RedisClient
from library.initializer.mysql_client import MysqlClient

lock = threading.RLock()


class Initializer(object):
    def __int__(self):
        self.logger = None or Log().get_logger()

    @retry()
    def init_redis(self, redis_config: dict = None):
        if redis_config is None:
            redis_config = config.redis_config
        try:
            redis_client = RedisClient(**redis_config).get_client()
            return redis_client
        except Exception as e:
            self.logger(e)
        return False

    @retry()
    def init_mysql(self, mysql_config: dict = None):

        if mysql_config is None:
            mysql_config = config.mysql_config

        try:
            mysql_client = MysqlClient(**mysql_config)
            return mysql_client
        except Exception as e:
            self.logger.exception(e)
        return False
