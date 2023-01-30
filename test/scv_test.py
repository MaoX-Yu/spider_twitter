# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/23 21:24
# @Brief   : 
# ===============================================================
from library.initializer.mysql_client import MysqlClient
from library.spider import BaseSpider
from library.log import Log

logger = Log().get_logger()


class RedisTest(BaseSpider):
    def __init__(self):
        super(RedisTest, self).__init__()

    def execute(self):
        sql = '''select * from twitter_reblogger_user'''
        data = self.mysql_client.read_df(sql)
        # self.logger.info(f'插入结果{self.status}')
        self.logger.info(f'查询结果:\n{data}')
        data.to_csv('被转发用户详情表.csv')


if __name__ == '__main__':
    spider = RedisTest()
    spider.execute()
