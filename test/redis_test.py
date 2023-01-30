# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 17:07
# @Brief   : 
# ===============================================================

import time

from library.config import redis_config
from library.initializer import initializer
from library.spider import BaseSpider
from library.log import Log

logger = Log().get_logger()
redis_client = initializer.Initializer().init_redis(redis_config)


class RedisTest(BaseSpider):
    def __init__(self):
        super(RedisTest, self).__init__()
        self.redis_key_todo = "twitter_test:TODO"

    def execute(self):
        self.logger.info('test ')
        seed = {'user_id': '2022/1/5', 'info_count': '22:44'}
        self.status = self.push_seeds(redis_key=self.redis_key_todo, seeds=seed)
        print(self.status)
        self.seed = self.get_seed()
        # self.logger.info(f"目前种子为：{self.seed}")
        if not self.seed:
            self.logger.info('种子队列为空')
            time.sleep(2)
            return self.seed
        self.logger.info(f"目前种子为：{self.seed}")


if __name__ == '__main__':
    spider = RedisTest()
    spider.execute()
