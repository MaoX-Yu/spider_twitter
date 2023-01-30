# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/19 22:41
# @Brief   : 网络关系图
# ===============================================================
import networkx as nx  # 导入networkx包
import matplotlib.pyplot as plt
import random

from library.initializer import initializer
from library.config import mysql_config as default_mysql_config


mysql_config = default_mysql_config
initializer = initializer.Initializer()
mysql_client = initializer.init_mysql(mysql_config)

sql = '''select `connect`, `depth` from twitter_user_connect'''
data = mysql_client.read_as_dict(sql)
# print(data)
G = nx.Graph()  # 生成一个BA无标度网络G
for info in data:
    G.add_edge(str(info['connect']).split('_')[0], str(info['connect']).split('_')[1])
pos = nx.spectral_layout(G)
nx.draw(G, pos,  node_size=30, width=0.1, alpha=0.5)  # 绘制网络G
# # plt.savefig("ba.png")           #输出方式1: 将图像存为一个png格式的图片文件
# print(G.edges())
plt.show()
