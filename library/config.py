# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 15:43
# @Brief   : 通用配置
# ===============================================================

import os

redis_config = {
    'host': os.getenv('REDIS_HOST', ''),  # redis 服务器
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 1)),
    'password': os.getenv('REDIS_PASS', ''),  # redis 密码
    'socket_timeout': os.getenv('REDIS_SOCKET_TIMEOUT', 600),
}

mysql_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'passwd': os.getenv('MYSQL_PASS', '123456'),
    'db': os.getenv('MYSQL_DB', 'spider'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True
}