# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 15:43
# @Brief   : redis 连接
# ===============================================================

import redis
from library import config


class RedisClient(object):

    def __init__(self, **kwargs):
        _config = {**config.redis_config, **kwargs}
        self.pool = redis.ConnectionPool(**_config)
        self.client = redis.Redis(connection_pool=self.pool)

    def get_client(self):
        return self.client
