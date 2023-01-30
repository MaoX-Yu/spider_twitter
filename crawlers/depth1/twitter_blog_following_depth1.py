# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @data    : 2022/1/6 22:44
# @Brief   : 用户关注列表,第一个深度取800
# ===============================================================
import json
import os
import time
import traceback
import requests
import urllib3

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
                'cookie': 'guest_id_marketing=v1%3A162632932618179575; guest_id_ads=v1%3A162632932618179575; _gid=GA1.2.198195989.1641115839; kdt=qoKcPEsE6NsF9GUtwTWtYQcN8XTBz9gV0Mdoz9I6; eu_cn=1; _ga_34PHSZMC42=GS1.1.1641136952.3.1.1641138720.0; _sl=1; mbox=PC#bca7aad0ec684b85bd03c300c925d936.32_0#1704884996|session#588f8c2c14774db6a50ddb23db07cab6#1641642055; _ga_BYKEBDM7DS=GS1.1.1641640182.2.1.1641640203.0; _ga=GA1.2.2082629645.1626329331; g_state={"i_l":0}; dnt=1; lang=en; personalization_id="v1_rdD73sCcbft+5Q0GPyjHag=="; guest_id=v1%3A164169632026578506; gt=1480007755625013248; auth_token=e927d772df6dc95b4dc4003e3216c30026d963f4; twid=u%3D1479802199022903297; ct0=78888ae9fc982ca14581e79f839f92974ba03d0de34cb8004dbf9574522da4a27a62221fd31e610750e166ed947ca5742920d0b1f9b5989f060c27d97ec84928524c4900d9a3f56993c36eec056f987b',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'x-csrf-token': '78888ae9fc982ca14581e79f839f92974ba03d0de34cb8004dbf9574522da4a27a62221fd31e610750e166ed947ca5742920d0b1f9b5989f060c27d97ec84928524c4900d9a3f56993c36eec056f987b'
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
            return resp, False

        try:
            json_data = json.loads(resp.text)
            data_info = json_data['data']['user']['result']['timeline']['timeline']['instructions']
            data = []
            depth = self.seed.get('depth', 1)
            cursor = ''
            for info in data_info:
                if 'TimelineAddEntries' == info['type']:
                    for following_info in info['entries']:
                        if 'cursor-bottom' in following_info['entryId']:
                            cursor = following_info['content']['value']
                        if 'TimelineTimelineItem' == following_info['content']['entryType']:
                            fl_info = following_info['content']['itemContent']['user_results']['result']
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
                        if int(self.seed.get('num', 0)) + len(data) >= 50:
                            break
            return data, cursor
        except Exception:
            self.logger.error(resp.text)
            self.logger.error(traceback.format_exc())
            return False, False

    def execute(self):
        self.seed = self.get_seed()
        if not self.seed:
            self.logger.info('种子队列为空')
            time.sleep(2)
            return self.seed
        self.logger.info(f"目前种子为：{self.seed}")
        spider_config = self.spider_config()
        resp = requests.get(**spider_config)  # http请求验证
        # self.logger.info(resp.text)
        data, cursor = self.parse(resp)
        self.logger.info(f'有效关注数{len(data)}')
        self.logger.info(f'下一页参数{cursor}')
        if data:
            self.logger.info(data)
            self.status = True
            self.insert_or_update(table_name='twitter_user_detail', data_list=data)  # 保存用户信息
            da = []
            for user_id in data:
                connect = f"{self.seed['blogger_id']}_{user_id['blogger_id']}"
                depth = self.seed.get('depth', 1)
                d = dict(
                    connect=connect,
                    from_id=self.seed['blogger_id'],
                    depth=depth
                )
                da.append(d)
            self.insert_or_update(table_name='twitter_user_connect', data_list=da)  # 保存关系表
            if int(self.seed.get('num', 0)) < 50:
                seed = {
                    'num': self.seed.get('num', 0) + len(data),
                    'cursor': cursor,
                    'blogger_id': self.seed['blogger_id'],
                    'is_cursor': 1,
                    'depth': 1
                }
                self.logger.info(f'下一页种子{seed}')
                self.push_seeds(redis_key=self.redis_key_todo, seeds=seed)  # 添加入redis队列
            else:
                self.logger.info('-----------------------------------')
                self.logger.info('深度1提取完毕！')
        else:
            self.status = False
        self.set_seed()

    def run(self):
        while True:
            self.execute()


if __name__ == '__main__':
    spider = SpiderTest()
    spider.run()
