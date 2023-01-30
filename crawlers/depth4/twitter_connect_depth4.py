# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/11 22:27
# @Brief   : 深度4关系爬取
# ===============================================================
import json
import os
import random
import threading
import time
import traceback
import requests
import urllib3
from requests import Response

from library.spider import BaseSpider
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SpiderTest(BaseSpider, threading.Thread):
    def __init__(self):
        super(SpiderTest, self).__init__()
        threading.Thread.__init__(self)
        self.redis_key_todo = "twitter_depth4:TODO"
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
                "count": 40,
                "withTweetQuoteCount": 'false',
                "includePromotedContent": 'false',
                "withSuperFollowsUserFields": 'true',
                "withBirdwatchPivots": 'false',
                "withDownvotePerspective": 'false',
                "withReactionsMetadata": 'false',
                "withReactionsPerspective": 'false',
                "withSuperFollowsTweetFields": 'true'
            }
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
            return resp, False

        try:
            range_num = random.randint(2, 10)
            json_data = json.loads(resp.text)
            if 'UserUnavailable' == json_data['data']['user']['result'].get('__typename'):
                return 0
            data_info = json_data['data']['user']['result']['timeline']['timeline']['instructions']
            data = []
            depth = self.seed.get('depth', 4)
            for info in data_info:
                if 'TimelineAddEntries' == info['type']:
                    for following_info in info['entries']:
                        if 'TimelineTimelineItem' == following_info['content']['entryType']:
                            fl_info = following_info['content']['itemContent']['user_results']['result']
                            if fl_info['__typename'] == 'UserUnavailable':
                                continue
                            blogger_num = fl_info['legacy']['statuses_count']
                            if blogger_num < int(os.getenv('BLOGGER_MAIN', 450)):
                                continue
                            blogger_id = fl_info.get('rest_id', '')
                            if not blogger_id:
                                continue
                            blogger_name = fl_info['legacy']['name']
                            blogger_str_id = fl_info['legacy']['screen_name']
                            desc = fl_info['legacy'].get('description', '')
                            location = fl_info['legacy'].get('location', '')
                            friends_count = fl_info['legacy'].get('friends_count', 0)
                            followers_count = fl_info['legacy'].get('followers_count', 0)
                            d = dict(
                                blogger_name=blogger_name,
                                blogger_str_id=blogger_str_id,
                                blogger_id=blogger_id,
                                blogger_num=blogger_num,
                                desc=desc,
                                location=location,
                                friends_count=friends_count,
                                followers_count=followers_count,
                                depth=depth
                            )
                            data.append(d)
                            if int(self.seed.get('num', 0)) + len(data) >= range_num:
                                break
            return data
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
        json_data = json.loads(resp.text)
        ret = json_data.get('errors', None)
        if not ret:
            return resp
        else:
            return False

    def execute(self):
        self.seed = self.get_seed()
        if not self.seed:
            self.logger.info('种子队列为空')
            time.sleep(2)
            return self.seed
        self.logger.info(f"目前种子为：{self.seed}")
        spider_config = self.spider_config()
        resp = self.get_and_check_resp(spider_config)  # http请求验证
        # self.logger.info(resp.text)
        if not resp:
            self.logger.info('-----------遇到风控------------')
            self.status = False
            self.set_seed()
            time.sleep(20)
        data = self.parse(resp)
        if data:
            self.logger.info(f'有效关注数{len(data)}')
            self.logger.info(data)
            self.status = True
            self.insert_or_update(table_name='twitter_user_detail', data_list=data, not_update_field=['depth'])  # 保存用户信息
            da = []
            for user_id in data:
                connect = f"{self.seed['blogger_id']}_{user_id['blogger_id']}"
                depth = self.seed.get('depth', 4)  # 深度
                d = dict(
                    connect=connect,
                    from_id=self.seed['blogger_id'],
                    depth=depth
                )
                da.append(d)
            self.insert_or_update(table_name='twitter_user_connect', data_list=da)  # 保存关系表
        self.set_seed()

    def run(self):
        while True:
            self.execute()


if __name__ == '__main__':
    start_type = int(os.getenv('START_TYPE', 1))  # 启动类型 0单进程 1多线程
    start_num = int(os.getenv('START_NUM', 3))  # 启动进线程数 默认为5
    if start_type == 0:
        spider = SpiderTest()
        spider.run()
    elif start_type == 1:
        thread_shared_list = list()
        for i in range(start_num):
            spider = SpiderTest()
            spider.start()
