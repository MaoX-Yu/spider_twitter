# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/4 23:30
# @Brief   : 获取用户详情,可以说最开始的入口在这。
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
        self.redis_key_todo = "twitter_depth_str_id:TODO"
        self.logger.info("开始计数")
        self.stime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.info(f'开始时间{self.stime}')

    def spider_config(self):
        try:
            # 1477573047549054983
            url = 'https://twitter.com/i/api/graphql/7mjxD3-C6BxitPMVQ6w0-Q/UserByScreenName'
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'cookie': 'guest_id_marketing=v1%3A162632932618179575; guest_id_ads=v1%3A162632932618179575; _gid=GA1.2.198195989.1641115839; g_state={"i_l":0}; kdt=qoKcPEsE6NsF9GUtwTWtYQcN8XTBz9gV0Mdoz9I6; eu_cn=1; _ga_34PHSZMC42=GS1.1.1641136952.3.1.1641138720.0; _ga_BYKEBDM7DS=GS1.1.1641296806.1.1.1641297033.0; _ga=GA1.2.2082629645.1626329331; mbox=PC#bca7aad0ec684b85bd03c300c925d936.32_0#1704383306|session#ee4b1b87005540f5b97abcbbc3e5a799#1641311666; lang=en; dnt=1; _sl=1; personalization_id="v1_gRwE/SKKfsFodIQjbIcxXw=="; guest_id=v1%3A164162529989436150; gt=1479709875928469506; auth_token=d25ce309a28190488f2585348e88a4932f87be51; ct0=6622870ffd46a2a022269cce7ef0f55225ee2d8f8db454f440ca8129c551474415c131ac21c9337780d48e138e29ab522620f95bc3616401c81a294c8da20fae8483e53f0864d9c06b3a345f71cd2235; twid=u%3D1477573047549054983',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'x-csrf-token': '6622870ffd46a2a022269cce7ef0f55225ee2d8f8db454f440ca8129c551474415c131ac21c9337780d48e138e29ab522620f95bc3616401c81a294c8da20fae8483e53f0864d9c06b3a345f71cd2235'
            }
            params = {
                "variables": json.dumps(
                    {
                        "screen_name": self.seed['blogger_str_id'],
                        "withSafetyModeUserFields": 'true',
                        "withSuperFollowsUserFields": 'true'
                    }
                )
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
            detail_info = json_data['data']['user']['result']['legacy']
            data = []
            blogger_num = detail_info['statuses_count']
            if blogger_num > int(os.getenv('BLOGGER_MAIN', 350)):
                blogger_name = detail_info['name']
                blogger_id = json_data['data']['user']['result']['rest_id']
                d = dict(
                    blogger_name=blogger_name,
                    blogger_id=blogger_id,
                    blogger_num=blogger_num,
                    blogger_str_id=self.seed['blogger_str_id'],
                    depth=self.seed['depth']
                )
                data.append(d)
            return data
        except Exception:
            self.logger.error(traceback.format_exc())
            return False

    def execute(self):
        self.seed = self.get_seed()
        if not self.seed:
            self.logger.info('种子队列为空')
            time.sleep(2)
            return self.seed
        self.logger.info(f"目前种子为：{self.seed}")
        spider_config = self.spider_config()
        resp = requests.get(**spider_config)  # http请求验证
        data = self.parse(resp)
        if data:
            self.logger.info(data)
            self.status = True
            # self.push_seeds(redis_key=self.redis_key_todo, seeds=date)  # 添加入redis队列
            # self.insert(table_name='twitter_user_detail', data_list=data)
        else:
            self.status = False
        self.set_seed()


if __name__ == '__main__':
    spider = SpiderTest()
    spider.execute()
