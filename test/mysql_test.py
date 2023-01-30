# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 18:08
# @Brief   : 
# ===============================================================

from library.config import redis_config
from library.initializer.mysql_client import MysqlClient
from library.spider import BaseSpider
from library.log import Log

logger = Log().get_logger()


class RedisTest(BaseSpider):
    def __init__(self):
        super(RedisTest, self).__init__()

    def execute(self):
        data_list = [{"key": "12", "value": "350"},
                     {"key": "13", "value": "350"},
                     {"key": "14", "value": "350"}]
        self.status = self.insert(table_name="test", data_list=data_list)
        sql = '''select * from test'''
        data = self.mysql_client.read_as_dict(sql)
        # self.logger.info(f'插入结果{self.status}')
        self.logger.info(f'查询结果{data}')


if __name__ == '__main__':
    spider = RedisTest()
    spider.execute()
