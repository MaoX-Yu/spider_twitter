# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/10 13:33
# @Brief   : 关系测试
# ===============================================================
import json
import os
import time
import traceback
import requests
import urllib3
from requests import Response

from library.spider import BaseSpider
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SpiderTest(BaseSpider):
    def __init__(self):
        super(SpiderTest, self).__init__()
        self.redis_key_todo = "twitter_depth1:TODO"
        self.logger.info("开始计数")
        self.stime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.info(f'开始时间{self.stime}')

    def spider_config(self):
        try:
            # 1477573047549054983
            url = 'https://twitter.com/i/api/graphql/Yj4Ft98o_Qd4UTqxJXvdOQ/Following'
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'cookie': 'guest_id_marketing=v1%3A162632932618179575; guest_id_ads=v1%3A162632932618179575; kdt=qoKcPEsE6NsF9GUtwTWtYQcN8XTBz9gV0Mdoz9I6; eu_cn=1; _ga_34PHSZMC42=GS1.1.1641136952.3.1.1641138720.0; mbox=PC#bca7aad0ec684b85bd03c300c925d936.32_0#1704884996|session#588f8c2c14774db6a50ddb23db07cab6#1641642055; _ga_BYKEBDM7DS=GS1.1.1641640182.2.1.1641640203.0; _ga=GA1.2.2082629645.1626329331; g_state={"i_l":0}; dnt=1; _gid=GA1.2.608517390.1641911114; lang=en; _sl=1; personalization_id="v1_rFH5F9Ro7IWA0FJ4GN5l9Q=="; guest_id=v1%3A164191301747337666; gt=1480916649645842437; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCHGApEl%252BAToMY3NyZl9p%250AZCIlMmUxYTIxNzRkMGM5ZTY4NDQ3MjcwMWIwOTAzYzY1MzA6B2lkIiU0ZWZm%250AMTRmOGNlMDI1NzkzYzBhMmY5OWNhNjA4NmZhNA%253D%253D--1bec4b19e3942fa18a7bbd84b78c364e9bb854fe; auth_token=204ded12d4cb46b09c5eb001e00a27468aebb241; twid=u%3D1479790778100912129; ct0=8fa23455688b8d5fab351f844a0fd3e0958968b5482353f0b34deb938b093a414eb7bd38fc3c483e15939af69284c8f5501b463a528096f5dcf33eef0ee4d395aa6f2f7dfd47853c68276dcc153ec28f; att=1-Zcjb3qYsTfadszuPeHeLegJwZ1aqaKqKXpP2SksP',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'x-csrf-token': '8fa23455688b8d5fab351f844a0fd3e0958968b5482353f0b34deb938b093a414eb7bd38fc3c483e15939af69284c8f5501b463a528096f5dcf33eef0ee4d395aa6f2f7dfd47853c68276dcc153ec28f'
            }
            variables = {
                "userId": self.seed['blogger_id'],
                "count": 5,
                "withTweetQuoteCount": 'false',
                "includePromotedContent": 'false',
                "withSuperFollowsUserFields": 'true',
                "withBirdwatchPivots": 'false',
                "withDownvotePerspective": 'false',
                "withReactionsMetadata": 'false',
                "withReactionsPerspective": 'false',
                "withSuperFollowsTweetFields": 'true'
            }
            is_cursor = self.seed.get('is_cursor', '')
            if is_cursor:
                variables['cursor'] = self.seed['cursor']
            params = {
                "variables": json.dumps(variables)
            }
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
            return resp

        try:
            json_data = json.loads(resp.text)
            data_info = json_data['data']['user']['result']['timeline']['timeline']['instructions']
            data = []
            cursor = ''
            for info in data_info:
                if 'TimelineAddEntries' == info['type']:
                    for following_info in info['entries']:
                        if 'cursor-bottom' in following_info['entryId']:
                            cursor = following_info['content']['value']
                        if 'TimelineTimelineItem' == following_info['content']['entryType']:
                            fl_info = following_info['content']['itemContent']['user_results']['result']
                            blogger_id = fl_info.get('rest_id', '')
                            if not blogger_id:
                                continue
                            blogger_name = fl_info['legacy']['name']
                            blogger_str_id = fl_info['legacy']['screen_name']
                            blogger_num = fl_info['legacy']['statuses_count']
                            if blogger_num < int(os.getenv('BLOGGER_MAIN', 400)):
                                continue
                            d = dict(
                                blogger_name=blogger_name,
                                blogger_str_id=blogger_str_id,
                                blogger_id=blogger_id,
                                blogger_num=blogger_num,
                                depth=1,
                                from_blogger_name=self.seed['blogger_name'],
                                from_blogger_id=self.seed['blogger_id']
                            )
                            data.append(d)
            return data, cursor

        except Exception:
            self.logger.error(resp.text)
            self.logger.error(traceback.format_exc())
            return False

    def get_and_check_resp(self, spider_config: dict = None):
        if not spider_config:
            return spider_config

        resp = requests.get(**spider_config)
        return self.check_resp(resp)

    def check_resp(self, resp):
        if not isinstance(resp, Response):
            return resp
        if resp.status_code == 429:
            self.logger.info('遇到风控')
            return False
        self.logger.info(resp)
        json_data = json.loads(resp.text)
        ret = json_data.get('errors', None)
        if not ret:
            return resp
        else:
            return False

    def execute(self):
        self.seed = {"blogger_id": "1434716980192419841"}
        spider_config = self.spider_config()
        resp = self.get_and_check_resp(spider_config)  # http请求验证
        self.logger.info(resp)
        exit()
        data, cursor = self.parse(resp)
        self.logger.info(f'有效关注数{len(data)}')
        self.logger.info(f'下一页参数{cursor}')
        if data:
            self.logger.info(data)
            self.status = True
            self.insert(table_name='twitter_user_detail', data_list=data)  # 添加入mysql保存备份
            if int(self.seed.get('num', 0)) < 800:
                seed = {
                    'num': self.seed.get('num', 0) + len(data),
                    'cursor': cursor,
                    'blogger_id': self.seed['blogger_id'],
                    'blogger_name': self.seed['blogger_name'],
                    'is_cursor': 1
                }
                self.logger.info(f'下一页种子{seed}')
                self.push_seeds(redis_key=self.redis_key_todo, seeds=seed)  # 添加入redis队列
            else:
                self.logger.info('-----------------------------------')
                self.logger.info('深度1提取完毕！')
                exit()
        else:
            self.status = False
        # self.set_seed()

    def run(self):
        self.execute()


if __name__ == '__main__':
    spider = SpiderTest()
    spider.run()
