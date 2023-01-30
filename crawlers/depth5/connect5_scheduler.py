# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/11 23:20
# @Brief   : 深度5调度
# ===============================================================
from library.spider import BaseSpider


class Scheduler(BaseSpider):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.redis_key_todo = "twitter_depth5:TODO"

    def execute(self):
        sql = '''select `blogger_id` from twitter_user_detail where `depth` = 4'''
        data = self.mysql_client.read_as_dict(sql)
        # self.logger.info(f'查询结果{data}')
        self.logger.info("开始调度")
        self.status = self.push_seeds(redis_key=self.redis_key_todo, seeds=data)
        self.logger.info(f"调度状态{self.status}")


if __name__ == '__main__':
    spider = Scheduler()
    spider.execute()
