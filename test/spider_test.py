# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 16:48
# @Brief   : 
# ===============================================================
import json
import time
import traceback

import requests

from library.initializer import redis_client
from library.spider import BaseSpider


class SpiderTest(BaseSpider):
    def __init__(self):
        super(SpiderTest, self).__init__(redis_client=redis_client)
        self.redis_key_todo = "twitter_test:TODO"
        self.redis_key_failed = 'twitter_test:FAILED'
        self.logger.info("开始计数")
        self.stime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.info(f'开始时间{self.stime}')
        self.test_count = 0
        self.rate = 5
        self.success = 0
        self.failed_num = 0

    def spider_config(self):
        try:
            url = 'https://twitter.com/i/api/graphql/QvCV3AU7X1ZXr9JSrH9EOA/UserTweets'
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'cookie': 'guest_id_marketing=v1%3A162632932618179575; guest_id_ads=v1%3A162632932618179575; _gid=GA1.2.198195989.1641115839; kdt=qoKcPEsE6NsF9GUtwTWtYQcN8XTBz9gV0Mdoz9I6; eu_cn=1; _ga_34PHSZMC42=GS1.1.1641136952.3.1.1641138720.0; _sl=1; mbox=PC#bca7aad0ec684b85bd03c300c925d936.32_0#1704884996|session#588f8c2c14774db6a50ddb23db07cab6#1641642055; _ga_BYKEBDM7DS=GS1.1.1641640182.2.1.1641640203.0; _ga=GA1.2.2082629645.1626329331; g_state={"i_l":0}; lang=en; dnt=1; gt=1479816024677847042; auth_multi="1479790778100912129:d37d0b67c14ec4a6308d4e91d7c04605d20bb41b"; auth_token=df5c00017404c43f0ee0d8fa5157fb1b2cceec26; twid=u%3D1479739346710577153; personalization_id="v1_0rCiCp4oL/TtpwLBITojSg=="; guest_id=v1%3A164165064930839597; ct0=6d3fbb57bb7d9ce8dac936a0f42e20f5ba915f556f5b90a941c7bd388257e4245f326aa79186d6c5b96bce99c255c5b6eedf4d3bf91523b4bb2ca755004d47ecb7c81ca023cce9e9f851016dc11d3dbd',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'x-csrf-token': '6d3fbb57bb7d9ce8dac936a0f42e20f5ba915f556f5b90a941c7bd388257e4245f326aa79186d6c5b96bce99c255c5b6eedf4d3bf91523b4bb2ca755004d47ecb7c81ca023cce9e9f851016dc11d3dbd'
            }
            params = {"variables": '''{"userId":"1349149096909668363","count":400,"withTweetQuoteCount":true,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withSuperFollowsUserFields":true,"withBirdwatchPivots":false,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":false}'''}
            return {
                'url': url,
                'headers': headers,
                'params': params,
                'verify': False,  # https请求忽略证书验证
                'timeout': 15
            }
        except Exception as e:
            self.logger.exception(e)
            return False

    def parse(self, resp):
        if not resp:
            return False

        try:
            json_data = json.loads(resp.text)
            data = []
            data_info = json_data['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries']
            self.logger.info(len(data_info))
            for info in data_info:
                if info['content']['entryType'] == 'TimelineTimelineItem':
                    item = info['content']['itemContent']['tweet_results']['result']
                    blog_id = item['rest_id']
                    blogger_id = item['core']['user_results']['result']['legacy']['screen_name']
                    blogger_name = item['core']['user_results']['result']['legacy']['name']
                    crated_time = item['legacy']['created_at']
                    blog_text = item['legacy']['full_text']
                    is_re = item['legacy']['retweeted']
                    d = dict(
                        blog_id=blog_id,
                        blogger_id=blogger_id,
                        blogger_name=blogger_name,
                        crated_time=crated_time,
                        blog_text=blog_text,
                        is_re=is_re,
                    )
                    data.append(d)
                    self.logger.info(d)
            return data
        except Exception:
            self.logger.info(traceback.format_exc())
            return False

    def execute(self):
        # 1476200441063129089
        spider_config = self.spider_config()
        resp = requests.get(**spider_config)  # http请求验证
        # self.logger.info(resp)
        data = self.parse(resp)
        self.logger.info(data)
        # print(resp.text)
        # self.logger.info(resp.text)


if __name__ == '__main__':
    spider = SpiderTest()
    spider.execute()
