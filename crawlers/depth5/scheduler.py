# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/9 10:24
# @Brief   : 深度5调度
# ===============================================================
from library.spider import BaseSpider


class Scheduler(BaseSpider):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.redis_key_todo = "twitter_blog_depth5:TODO"

    def execute(self):
        # 1.16 0，1000
        # 1.17 1000,1000
        # 1.18 2000,1500
        sql = '''select `blogger_id`,`blogger_name` from twitter_user_detail where `depth` = 5 limit 3500,2000'''
        data = self.mysql_client.read_as_dict(sql)
        self.logger.info(f'查询结果{data},个数{len(data)}')
        self.logger.info("开始调度")
        self.status = self.push_seeds(redis_key=self.redis_key_todo, seeds=data)
        self.logger.info(f"调度状态{self.status}")


if __name__ == '__main__':
    spider = Scheduler()
    spider.execute()
