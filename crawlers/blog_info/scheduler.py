# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/8 13:12
# @Brief   : 博文详情调度
# ===============================================================
from library.spider import BaseSpider


class Scheduler(BaseSpider):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.redis_key_todo = "twitter_blog_depth1:TODO"

    def execute(self):
        sql = '''select `blogger_id`, `blogger_name` from twitter_user_detail where `depth` = 1'''
        data = self.mysql_client.read_as_dict(sql)
        # self.logger.info(f'查询结果{data}')
        self.logger.info("开始调度")
        self.status = self.push_seeds(redis_key=self.redis_key_todo, seeds=data)
        self.logger.info(f"调度状态{self.status}")


if __name__ == '__main__':
    spider = Scheduler()
    spider.execute()
