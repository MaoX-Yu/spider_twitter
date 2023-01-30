# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/9 17:24
# @Brief   : 详情测试
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
            # url = 'https://twitter.com/i/api/graphql/7mjxD3-C6BxitPMVQ6w0-Q/UserByScreenName'
            # url = 'https://twitter.com/i/api/graphql/Yj4Ft98o_Qd4UTqxJXvdOQ/Following'
            url = 'https://twitter.com/i/api/graphql/ndTsAcr5shJTi2ZyBk5jQw/TweetDetail'
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'cookie': 'guest_id_marketing=v1%3A162632932618179575; guest_id_ads=v1%3A162632932618179575; _gid=GA1.2.198195989.1641115839; kdt=qoKcPEsE6NsF9GUtwTWtYQcN8XTBz9gV0Mdoz9I6; eu_cn=1; _ga_34PHSZMC42=GS1.1.1641136952.3.1.1641138720.0; _sl=1; mbox=PC#bca7aad0ec684b85bd03c300c925d936.32_0#1704884996|session#588f8c2c14774db6a50ddb23db07cab6#1641642055; _ga_BYKEBDM7DS=GS1.1.1641640182.2.1.1641640203.0; _ga=GA1.2.2082629645.1626329331; g_state={"i_l":0}; dnt=1; lang=en; personalization_id="v1_rdD73sCcbft+5Q0GPyjHag=="; guest_id=v1%3A164169632026578506; gt=1480007755625013248; auth_token=e927d772df6dc95b4dc4003e3216c30026d963f4; twid=u%3D1479802199022903297; ct0=78888ae9fc982ca14581e79f839f92974ba03d0de34cb8004dbf9574522da4a27a62221fd31e610750e166ed947ca5742920d0b1f9b5989f060c27d97ec84928524c4900d9a3f56993c36eec056f987b',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'x-csrf-token': '78888ae9fc982ca14581e79f839f92974ba03d0de34cb8004dbf9574522da4a27a62221fd31e610750e166ed947ca5742920d0b1f9b5989f060c27d97ec84928524c4900d9a3f56993c36eec056f987b'
            }
            # params = {
            #     "variables": json.dumps(
            #         {
            #             "screen_name": 'sakamatachloe',
            #             "withSafetyModeUserFields": 'true',
            #             "withSuperFollowsUserFields": 'true'
            #         }
            #     )
            # }

            # variables = {
            #     "userId": '1433669866406375432',
            #     "count": 30,
            #     "withTweetQuoteCount": 'false',
            #     "includePromotedContent": 'false',
            #     "withSuperFollowsUserFields": 'true',
            #     "withBirdwatchPivots": 'false',
            #     "withDownvotePerspective": 'false',
            #     "withReactionsMetadata": 'false',
            #     "withReactionsPerspective": 'false',
            #     "withSuperFollowsTweetFields": 'true'
            # }

            # params = {
            #     "variables": json.dumps(variables)
            # }

            params = {
                '''include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&include_ext_sensitive_media_warning=true&send_error_codes=true&simple_quoted_tweet=true&q=(from:sakamatachloe) until:2022-01-01 since:2021-01-01&tweet_search_mode=live&count=20&query_source=typed_query&pc=1&spelling_corrections=1&ext=mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,superFollowMetadata'''
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
            # detail_info = json_data['data']['user']['result']['legacy']
            data = []
            # blogger_num = detail_info['statuses_count']
            # if blogger_num > int(os.getenv('BLOGGER_MAIN', 350)):
            #     blogger_name = detail_info['name']
            #     blogger_id = json_data['data']['user']['result']['rest_id']
            #     d = dict(
            #         blogger_name=blogger_name,
            #         blogger_id=blogger_id,
            #         blogger_num=blogger_num,
            #         blogger_str_id=self.seed['blogger_str_id'],
            #         depth=self.seed['depth']
            #     )
            #     data.append(d)
            return data
        except Exception:
            self.logger.error(traceback.format_exc())
            return False

    def execute(self):
        spider_config = self.spider_config()
        resp = requests.get(**spider_config)  # http请求验证
        self.logger.info(resp.text)
        # data = self.parse(resp)
        # if data:
        #     self.logger.info(data)
        #     self.status = True
            # self.push_seeds(redis_key=self.redis_key_todo, seeds=date)  # 添加入redis队列
            # self.insert(table_name='twitter_user_detail', data_list=data)
        # else:
        #     self.status = False


if __name__ == '__main__':
    spider = SpiderTest()
    spider.execute()
