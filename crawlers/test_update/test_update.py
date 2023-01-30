# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/16 13:15
# @Brief   : 更新测试
# ===============================================================
from library.spider import BaseSpider


class SpiderTest(BaseSpider):
    def __init__(self):
        super(SpiderTest, self).__init__()

    def execute(self):
        sql = '''SELECT * FROM twitter_blog_info_new WHERE crated_time LIKE "%2022%"'''
        data = self.mysql_client.read_as_dict(sql)
        # data['crated_time'] = data['crated_time'].replace('2009', '2000')
        self.logger.info(len(data))
        for info in data:
            self.logger.info(info)
            info['crated_time'] = str(info['crated_time']).replace('2022', '2021').replace('Mon ', '').\
                replace('Tue ', '').replace('Wed ', '').replace('Thu ', '').replace('Fri ', '').\
                replace('Sat ', '').replace('Sun ', '')
            self.logger.info(info)
            self.insert_or_update(table_name='twitter_blog_info_new', data_list=info, not_update_field=['depth'])
            # break
        # self.insert_or_update(table_name='test', data_list=data, not_update_field=['depth'])


if __name__ == '__main__':
    spider = SpiderTest()
    spider.execute()

