# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/8 21:37
# @Brief   : 深度3爬取
# ===============================================================
import json
import os
import threading
import time
import traceback
import requests
import urllib3
from requests import Response

from library.spider import BaseSpider
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Spider(BaseSpider, threading.Thread):
    def __init__(self):
        super(Spider, self).__init__()
        threading.Thread.__init__(self)
        self.redis_key_todo = "twitter_blog_depth3:TODO"
        self.logger.info("开始计数")
        self.stime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.info(f'开始时间{self.stime}')

    def spider_config(self):
        try:
            url = 'https://twitter.com/i/api/graphql/QvCV3AU7X1ZXr9JSrH9EOA/UserTweets'
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'cookie': 'guest_id_marketing=v1%3A162632932618179575; guest_id_ads=v1%3A162632932618179575; kdt=qoKcPEsE6NsF9GUtwTWtYQcN8XTBz9gV0Mdoz9I6; eu_cn=1; _ga_34PHSZMC42=GS1.1.1641136952.3.1.1641138720.0; mbox=PC#bca7aad0ec684b85bd03c300c925d936.32_0#1704884996|session#588f8c2c14774db6a50ddb23db07cab6#1641642055; _ga_BYKEBDM7DS=GS1.1.1641640182.2.1.1641640203.0; _ga=GA1.2.2082629645.1626329331; g_state={"i_l":0}; dnt=1; _gid=GA1.2.608517390.1641911114; _sl=1; lang=en; personalization_id="v1_B7qjDlDqA44FHAeJgJ++KQ=="; guest_id=v1%3A164199261134741677; gt=1481250491841482754; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCL4WY05%252BAToMY3NyZl9p%250AZCIlYjJiMzIxZTljMTYxZDQwZWI1YTQ5YjU0NjVjNzk5Y2I6B2lkIiVlMjE3%250ANDBmYmJjZWI0YzE2YzhhYWIwODE5MmMwZjViOA%253D%253D--45f2bf1cf86a520fb1ccbdab83b88c6455f7923e; auth_token=a294b5d77ba4a0d846959004b77f7ae7ce57468a; ct0=73fe3205758fa6915b9bebed158ce0c9683bccbd34c40dccb4d55b8094e4d29f6c008f06dbf5dc67ced2609309e90ca1d0229ce6e2599e1ea616c8abde79c50c3a38764a8cf1a537fb2e7a31b755e594; twid=u%3D1481239087336267778; att=1-3gfq2EpwNLOmGCSHuVctulxrVuFYbIABVzKk2Ssq',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'x-csrf-token': '73fe3205758fa6915b9bebed158ce0c9683bccbd34c40dccb4d55b8094e4d29f6c008f06dbf5dc67ced2609309e90ca1d0229ce6e2599e1ea616c8abde79c50c3a38764a8cf1a537fb2e7a31b755e594'
            }
            variables = {
                "userId": self.seed['blogger_id'],
                "count": 80,
                "withTweetQuoteCount": 'true',
                "includePromotedContent": 'true',
                "withQuickPromoteEligibilityTweetFields": 'true',
                "withSuperFollowsUserFields": 'true',
                "withBirdwatchPivots": 'false',
                "withDownvotePerspective": 'false',
                "withReactionsMetadata": 'false',
                "withReactionsPerspective": 'false',
                "withSuperFollowsTweetFields": 'true',
                "withVoice": 'true',
                "withV2Timeline": 'false'
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
            return False, False

        try:
            json_data = json.loads(resp.text)
            data = []
            cursor = ''
            data_info = json_data['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries']
            for info in data_info:
                if 'cursor-bottom' in info['entryId']:
                    cursor = info['content']['value']
                if info['content']['entryType'] == 'TimelineTimelineItem':
                    item = info['content']['itemContent']['tweet_results'].get('result', '')
                    if not item:
                        continue
                    blog_id = item.get('rest_id', '')
                    if not blog_id:
                        continue
                    blogger_str_id = item['core']['user_results']['result']['legacy']['screen_name']
                    blogger_name = item['core']['user_results']['result']['legacy']['name']
                    crated_time = item['legacy']['created_at']
                    blog_text = item['legacy']['full_text']
                    blog_text = str(blog_text).split('https://t.co/')[0]
                    is_re = 'false'
                    re_blogger_name = ''
                    re_blogger_screen_name = ''
                    depth = self.seed.get('depth', 3)
                    if "RT @" in blog_text:
                        is_re = 'true'
                        re_item = item['legacy'].get('retweeted_status_result', '')
                        if re_item:
                            re_blogger_screen_name = item['legacy']['retweeted_status_result']['result']['core']['user_results']['result']['legacy']['screen_name']
                            re_blogger_name = item['legacy']['retweeted_status_result']['result']['core']['user_results']['result']['legacy']['name']
                    d = dict(
                        blog_id=blog_id,
                        blogger_str_id=blogger_str_id,
                        blogger_name=blogger_name,
                        crated_time=crated_time,
                        blog_text=blog_text,
                        is_re=is_re,
                        re_blogger_screen_name=re_blogger_screen_name,
                        re_blogger_name=re_blogger_name,
                        depth=depth
                    )
                    data.append(d)
            return data, cursor
        except Exception:
            self.logger.info(traceback.format_exc())
            self.logger.error(resp.text)
            return False

    def get_and_check_resp(self, spider_config: dict = None):
        if not spider_config:
            return spider_config

        try:
            resp = requests.get(**spider_config)
            return self.check_resp(resp)
        except Exception as e:
            self.logger.info(e)
            return False

    def check_resp(self, resp):
        if not isinstance(resp, Response):
            return resp
        if resp.status_code == 429:
            return False
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
        data, cursor = self.parse(resp)
        if data:
            self.logger.info(f'下一页参数:{cursor}')
            self.logger.info(f'博文数量{len(data)}')
            self.logger.info(data)
            self.status = True
            self.insert_or_update(table_name='twitter_blog_info', data_list=data, not_update_field=['depth'])  # 添加入mysql保存备份
            num = int(self.seed.get('num', 0)) + len(data)
            if num < 380:
                seed = {
                    'num': num,
                    'cursor': cursor,
                    'blogger_id': self.seed['blogger_id'],
                    'blogger_name': self.seed['blogger_name'],
                    'is_cursor': 1
                }
                self.logger.info(f'下一页种子{seed}')
                self.status = self.push_seeds(redis_key=self.redis_key_todo, seeds=seed)  # 添加入redis队列
                self.set_seed()
            else:
                self.logger.info('-----------------------------------')
                self.logger.info('深度3博文采集完毕！')
            self.set_seed()
        else:
            self.logger.info('遇到风控，稍后重试')
            self.status = False
            self.set_seed()
            time.sleep(2)

    def run(self):
        while True:
            self.execute()


if __name__ == '__main__':
    start_type = int(os.getenv('START_TYPE', 1))  # 启动类型 0单进程 1多线程
    start_num = int(os.getenv('START_NUM', 7))  # 启动进线程数 默认为5
    if start_type == 0:
        spider = Spider()
        spider.run()
    elif start_type == 1:
        thread_shared_list = list()
        for i in range(start_num):
            spider = Spider()
            spider.start()
