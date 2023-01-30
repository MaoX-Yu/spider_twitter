# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 22:29
# @Brief   : 
# ===============================================================

import traceback

import pandas
import pymysql
from retrying import retry

from library.log import Log

logger = Log().get_logger()


class MysqlClient(object):

    def __init__(self, **kwargs):

        self.mysql_config = kwargs
        self.connection = self._connect_mysql()

    def _connect_mysql(self):
        self.connection = None
        self.connection = pymysql.connect(**self.mysql_config)
        return self.connection

    def reconnect(self):
        self._connect_mysql()

    @retry()
    def read_as_dict(self, sql):
        try:
            with self.connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
            return data or None
        except:
            self.reconnect()
            logger.warning(traceback.format_exc())
            return False

    @retry()
    def read_df(self, sql):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                columns = [x[0] for x in cursor.description]

            if not isinstance(data, (list, tuple)):
                return None
            return pandas.DataFrame(list(data), columns=columns)
        except:
            self.reconnect()
            logger.warning(traceback.format_exc())
            return False

    @retry()
    def write(self, sql, *args):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, *args)
                self.connection.commit()
            return True
        except:
            self.reconnect()
            logger.warning(traceback.format_exc())
            return False

    @retry()
    def write_many(self, sql, *args):
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(sql, *args)
                self.connection.commit()
            return True
        except:
            self.reconnect()
            logger.warning(traceback.format_exc())
            return False
