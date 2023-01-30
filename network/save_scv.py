# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/19 23:40
# @Brief   : 保存关系
# ===============================================================
import csv

from library.initializer import initializer
from library.config import mysql_config as default_mysql_config

mysql_config = default_mysql_config
initializer = initializer.Initializer()
mysql_client = initializer.init_mysql(mysql_config)

sql = '''select `connect`, `depth` from twitter_user_connect'''
data = mysql_client.read_as_dict(sql)
da = []
c = ['c1', 'c2']
# print(data)
for info in data:
    a = str(info['connect']).split('_')[0]
    b = str(info['connect']).split('_')[1]
    d = [a, b]
    da.append(d)
with open('connect.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(c)
    w.writerows(da)

