# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/7 22:30
# @Brief   : 调度，即最开始的用户
# ===============================================================
from library.spider import BaseSpider


class Scheduler(BaseSpider):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.redis_key_todo = "twitter_depth_str_id:TODO"

    def execute(self):
        self.logger.info("开始调度")
        seed = {'blogger_str_id': 'amyklobuchar', 'depth': '0'}
        self.status = self.push_seeds(redis_key=self.redis_key_todo, seeds=seed)
        self.logger.info(f"调度状态{self.status}")


if __name__ == '__main__':
    spider = Scheduler()
    spider.execute()
