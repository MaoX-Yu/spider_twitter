# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/8 14:26
# @Brief   : 深度2-6用户的爬取
# ===============================================================
import json
import os
import threading
import time
import traceback
import requests
import urllib3

from library.spider import BaseSpider
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Spider(BaseSpider, threading.Thread):
    def __init__(self):
        super(Spider, self).__init__()
        threading.Thread.__init__(self)
        self.redis_key_todo = "twitter_depth_2-6:TODO"
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
                'cookie': 'guest_id_marketing=v1%3A162632932618179575; guest_id_ads=v1%3A162632932618179575; _gid=GA1.2.198195989.1641115839; kdt=qoKcPEsE6NsF9GUtwTWtYQcN8XTBz9gV0Mdoz9I6; eu_cn=1; _ga_34PHSZMC42=GS1.1.1641136952.3.1.1641138720.0; lang=en; _sl=1; gt=1479746712218771460; g_state={"i_l":0}; personalization_id="v1_GWW7tO9KxtQwmjZ1syGF/A=="; guest_id=v1%3A164164015259472732; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCErlYDl%252BAToMY3NyZl9p%250AZCIlY2RlMzljNzBhMGZlMDM2ZDkxMDRlZWYyYmNjOTUzNDA6B2lkIiViMjUw%250AMWRjOTBlZjUyZmNlMjRlMDdlMWFkN2NiMDE5MQ%253D%253D--fa962e98d345c90a18ab56a2262064b53ae9e113; auth_token=1ec18166a8e006f0163c8c200e181c4cda0078f6; ct0=b90d298573878da5d02068042b42d234f4c33829fd9fe4f842313be51cb58089bdcbf728d4a57d1740ea5284f0a8a3412458e0acb27589f7e8e1154e7aa52cdf10a85c957d60e749bb6f6684dcfffc38; twid=u%3D1479739346710577153; _ga=GA1.1.2082629645.1626329331; at_check=true; mbox=PC#bca7aad0ec684b85bd03c300c925d936.32_0#1704884996|session#588f8c2c14774db6a50ddb23db07cab6#1641642055; _ga_BYKEBDM7DS=GS1.1.1641640182.2.1.1641640203.0; external_referer=padhuUp37ziQmniu9x3JVcF9brOmpu5e|0|8e8t2xd8A2w%3D',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'x-csrf-token': 'b90d298573878da5d02068042b42d234f4c33829fd9fe4f842313be51cb58089bdcbf728d4a57d1740ea5284f0a8a3412458e0acb27589f7e8e1154e7aa52cdf10a85c957d60e749bb6f6684dcfffc38'
            }
            variables = {
                "userId": self.seed['blogger_id'],
                "count": 30,
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
            depth = self.seed['depth'] + 1
            if depth >= 7:
                return depth
            for info in data_info:
                if 'TimelineAddEntries' == info['type']:
                    for following_info in info['entries']:
                        data = []
                        in_status = False
                        if 'TimelineTimelineItem' == following_info['content']['entryType']:
                            fl_info = following_info['content']['itemContent']['user_results']['result']
                            blogger_id = fl_info.get('rest_id', '')
                            if not blogger_id:
                                continue
                            blogger_name = fl_info['legacy']['name']
                            blogger_str_id = fl_info['legacy']['screen_name']
                            blogger_num = fl_info['legacy']['statuses_count']
                            if blogger_num < int(os.getenv('BLOGGER_MAIN', 350)):
                                continue
                            d = dict(
                                blogger_name=blogger_name,
                                blogger_str_id=blogger_str_id,
                                blogger_id=blogger_id,
                                blogger_num=blogger_num,
                                depth=depth,
                                from_blogger_name=self.seed['blogger_name'],
                                from_blogger_id=self.seed['blogger_id']
                            )
                            da = dict(
                                blogger_name=blogger_name,
                                blogger_id=blogger_id,
                                blogger_num=blogger_num,
                                depth=depth,
                            )
                            data.append(da)
                            self.logger.info(f"当前种子{self.seed['blogger_name']}")
                            in_status = self.insert(table_name='twitter_user_detail', data_list=d)
                        if in_status:
                            self.logger.info('--------success---------')
                            break
            return data
        except Exception:
            self.logger.error(resp.text)
            self.logger.error(traceback.format_exc())
            return False

    def execute(self):
        self.seed = self.get_seed()
        if not self.seed:
            self.logger.info('种子队列为空')
            time.sleep(2)
            return self.seed
        self.logger.info(f"目前种子为：{self.seed}")
        depth = self.seed['depth'] + 1
        if depth < 7:
            spider_config = self.spider_config()
            resp = requests.get(**spider_config)  # http请求验证
            # self.logger.info(resp.text)
            data = self.parse(resp)
            if data:
                self.status = True
                if not isinstance(data, int):
                    redis_status = self.push_seeds(redis_key=self.redis_key_todo, seeds=data)
                    self.logger.info(f'redis添加状态{redis_status}')
            else:
                self.status = False
                self.logger.info('遇到风控')
                time.sleep(30)
                self.set_seed()
        self.set_seed()


    def run(self):
        while True:
            self.execute()


if __name__ == '__main__':
    start_type = int(os.getenv('START_TYPE', 1))  # 启动类型 0单进程 1多线程
    start_num = int(os.getenv('START_NUM', 3))  # 启动进线程数 默认为5
    if start_type == 0:
        spider = Spider()
        spider.run()
    elif start_type == 1:
        thread_shared_list = list()
        for i in range(start_num):
            spider = Spider()
            spider.start()
