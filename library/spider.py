# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : double
# @Date    : 2022/1/3 16:00
# @Brief   : 爬虫基类
# ===============================================================

import json
import os
import time

import pandas
from pandas import DataFrame
from retrying import retry

from library.config import redis_config as default_redis_config, \
    mysql_config as default_mysql_config
from library.initializer import initializer
from library import log


class BaseSpider(object):
    def __init__(self, mysql_config: dict = None, mysql_client=None, redis_config: dict = None, redis_client=None, logger=None):
        self.redis_config = redis_config or default_redis_config  # redis 配置
        self.mysql_config = mysql_config or default_mysql_config

        self.logger = logger or log.Log().get_logger()  # 日志初始化
        self.initializer = initializer.Initializer()
        self.redis_client = redis_client or self.initializer.init_redis(self.redis_config)  # redis 客户端
        self.mysql_client = mysql_client or self.initializer.init_mysql(self.mysql_config)
        self.redis_key_todo = None  # 读存redis队列名字
        self.seed = None  # 种子数据
        self.status = None  # 爬取的状态
        self.start_time = None
        self.request_counter: int = 0  # 请求数
        self.request_oe_counter: int = 0  # 其他错误计数
        self.request_count_saved_time: int = int(time.time())
        self.seed_max_failed_count = int(os.getenv('SEED_MAX_FAILED_COUNT', 6))

    def get_seed(self, redis_key_todo: str = None, position: str = 'RIGHT', seed: dict = None):
        value = None
        self.status = None
        self.start_time = time.perf_counter()
        if seed:
            return seed
        seed = None
        try:
            if redis_key_todo is None:
                redis_key_todo = self.redis_key_todo
            if position == 'RIGHT':
                value = self.redis_client.rpop(redis_key_todo)
            else:
                value = self.redis_client.lpop(redis_key_todo)
            if isinstance(value, (str, bytes)) and len(value) > 0:
                seed = json.loads(value)
        except json.JSONDecodeError as je:
            self.logger.error(f"{je}: parse json error -- {value}")
        except Exception as e:
            self.logger.exception(e)


        return seed

    def set_seed(self, status: bool = None, seed: dict = None, redis_key_todo: str = None,
                 position: str = 'LEFT'):
        try:
            if seed is None:
                seed = self.seed
                if seed is None:
                    return None
            if redis_key_todo is None:
                redis_key_todo = self.redis_key_todo
            if status is None:
                status = self.status
            if status is False:
                fail_num = int(seed.get('fail_num', 0)) + 1
                if fail_num >= self.seed_max_failed_count:
                    # 处理异常种子
                    seed['fail_num'] = 0
                    seed['tfn'] = seed.get('tfn', 0) + fail_num
                    self.redis_client.lpush(redis_key_todo.replace('TODO', 'FAILED'), json.dumps(seed))
                    return True
                seed['fail_num'] = fail_num
                if position == 'LEFT':
                    self.redis_client.lpush(redis_key_todo, json.dumps(seed))
                else:
                    self.redis_client.rpush(redis_key_todo, json.dumps(seed))
                return True
            return None
        except Exception as e:
            self.logger.exception(e)
            return False

    @retry()
    def push_seeds(self, seeds, redis_key: str, position: str = 'LEFT'):
        if not seeds or not redis_key:
            return False
        if not isinstance(seeds, (list, dict)):
            raise Exception('seeds must be list or dict.')
        if isinstance(seeds, dict):
            seeds = [seeds]
        json_list = [json.dumps(seed, ensure_ascii=False) for seed in seeds]
        try:
            if position == 'RIGHT':
                self.redis_client.rpush(redis_key, *json_list)
            else:
                self.redis_client.lpush(redis_key, *json_list)
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    @retry()
    def insert_or_update(self, table_name: str, data_list=None, not_update_field: list = list(), insert_key: str = 'into'):
        if not data_list:
            return data_list

        if not isinstance(data_list, (list, dict)):
            self.logger.warning('insert data must be list or dict.')
            return False

        if isinstance(data_list, list) and not data_list[0]:
            return data_list[0]

        datas = data_list
        if isinstance(datas, dict):
            # 字典转列表
            datas = [datas]

        try:
            # data_df = DataFrame(data_list)
            data_df = DataFrame(datas).where((pandas.notnull(DataFrame(datas))), None)  # 处理字段是NULL的情况
            column_str = ','.join(f'`{field}`' for field in data_df.columns)
            value_str = ','.join(['%s'] * len(data_df.columns))

            update_list = list()
            for column in data_df.columns:
                if column in not_update_field:
                    continue
                update_list.append('`{field}`=VALUES(`{field}`)'.format(field=column))
            update_str = ','.join(update_list)
            if '.' in table_name:
                table_name = table_name.split('.')
                table_name = f"`{table_name[0].replace('`', '')}`.`{table_name[1].replace('`', '')}`"
            else:
                table_name = f"`{table_name}`"

            if insert_key.upper() == 'IGNORE':
                sql = f"INSERT IGNORE {table_name} ({column_str}) VALUES({value_str})"
            else:
                sql = f"INSERT INTO {table_name} ({column_str}) VALUES({value_str}) " \
                      f"ON DUPLICATE KEY UPDATE {update_str}"
            result = self.mysql_client.write_many(sql, data_df.values.tolist())
            return result

        except Exception as e:
            self.logger.exception(e)
            return False
