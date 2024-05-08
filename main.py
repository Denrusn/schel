# -*- coding: utf-8 -*-
import requests
import random
import time
from lxml import etree
import pandas as pd
import pytz
from datetime import datetime, timedelta
from prettytable import from_csv
from io import StringIO
import os
import logging

# 1、创建一个logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)
# 2、创建一个handler，用于写入日志文件
# fh = logging.FileHandler('test.log')
# fh.setLevel(logging.DEBUG)
# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# 3、定义handler的输出格式（formatter）
formatter = logging.Formatter('%(message)s')
# 4、给handler添加formatter
# fh.setFormatter(formatter)
ch.setFormatter(formatter)
# 5、给logger添加handler
# logger.addHandler(fh)
logger.addHandler(ch)


def export_df_to_table(dataframe):
    """工具函数：将dataframe的表格输出为 prettytable 表示的表格"""
    output = StringIO()
    dataframe.to_csv(output)
    output.seek(0)
    string_value = from_csv(output)
    return string_value


class HupuSpider(object):

    def __init__(self):
        super(object).__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://www.zhibo8.com",
            "Referer": "https://www.zhibo8.com/",

        }

    def home_page(self):
        url = "https://dingshi4pc.qiumibao.com/livetext/data/cache/livetext/1265774/0/lit_page_2/1538.htm?get=%s" \
              % random.random()
        res = requests.get(url, headers=self.headers)
        print(res.text)
        print(res.json())


class Zhiboba(object):
    def __init__(self):
        super(object).__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://www.zhibo8.com",
            "Referer": "https://www.zhibo8.com/",

        }

    def main(self, date='2024-01-10', game_id='1231142', sid_no_change_limit=10):
        self.home_page()
        # game_id = str(input("请输入比赛ID："))
        self.live(date, game_id, sid_no_change_limit)

    def home_page(self):
        '''
        主页，获取赛事game_id
        :return:
        '''

        def remove_el(data_list, *args):
            for el in args:
                try:
                    data_list.remove(el)
                except Exception:
                    continue
            return data_list

        url = "https://www.zhibo8.com/"
        res = requests.get(url, headers=self.headers, verify=False)
        html = etree.HTML(res.content.decode())
        basketball_li = html.xpath("//div[@class='_content']//li[@data-type='basketball']")
        basketball_info = list(map(lambda x: dict(x.attrib), basketball_li))
        df = pd.DataFrame(basketball_info)
        df['id'] = df['id'].apply(lambda x: x[6:])
        df = df[df['label'].apply(lambda x: "NBA" in x or "CBA" in x)]
        # df['label'] = df['label'].apply(lambda x: ','.join(remove_el(x.split(','), 'NBA', '篮球')))
        df['label'] = df['label'].apply(lambda x: ','.join(remove_el(x.split(','), '篮球', '中国篮球')))
        df['data-time'] = pd.to_datetime(df['data-time'])

        shanghai_tz = pytz.timezone('Asia/Shanghai')
        utc_tomorrow = datetime.now() + timedelta(days=1)
        beijing_tomorrow = utc_tomorrow.astimezone(shanghai_tz).strftime("%Y-%m-%d") + " 23:59:59"
        df = df[df['data-time'] <= beijing_tomorrow]
        df = df.loc[:, ['label', 'data-time', 'id']]
        df_str = export_df_to_table(df)
        logger.info(f'{df_str}')

    def live(self, date='2024-01-10', game_id="1231142", sid_no_change_limit=10):
        # 获取最大信号max_sid
        max_sid = self.get_live_max_sid(game_id)
        logger.info(f'{max_sid}')

        # 往前查30个sid
        for i in range(max_sid - 30, max_sid + 1):
            live_data = self.get_live_data_by_sid(game_id, i)
            if not live_data:
                continue
            game_time = self.get_game_time(date, game_id)
            self.live_format(live_data, game_time)

        start_sid = max_sid
        sid_no_change = 0  # sid没变化情况计数
        while True:
            end_sid = self.get_live_max_sid(game_id)
            if end_sid > start_sid:
                for i in range(start_sid + 1, end_sid + 1):
                    live_data = self.get_live_data_by_sid(game_id, i)
                    if not live_data:
                        continue
                    game_time = self.get_game_time(date, game_id)
                    self.live_format(live_data, game_time)
                start_sid = end_sid
                sid_no_change = 0
            else:
                sid_no_change += 1
                time.sleep(2)

            if sid_no_change > sid_no_change_limit:
                # 如果sid没变化超过限制次数则退出循环
                logger.info(f'SID No Change。。。')
                logger.info(f'EXIT!')
                break

    def get_live_data_by_sid(self, game_id, sid):
        item_url = f"https://dingshi4pc.qiumibao.com/livetext/data/cache/livetext" \
                   f"/{game_id}/0/lit_page_2/{sid}.htm?get={random.random()}"
        res = requests.get(item_url, headers=self.headers)
        live_data = []
        if res.status_code != 200:
            return live_data
        live_data = res.json()
        return live_data

    def get_live_max_sid(self, game_id):
        # 获取最大信号max_sid
        sid_url = f'https://dingshi4pc.qiumibao.com/livetext/data/cache/max_sid/{game_id}/0.htm?time={random.random()}'
        res = requests.get(sid_url, headers=self.headers)
        max_sid = int(res.text)
        return max_sid

    @staticmethod
    def live_format(data, game_time):
        for item in data:
            try:
                user_chn = item.get("user_chn")
                live_text = item.get("live_text")
                live_time = item.get("live_time")[11:]
                left_score = item.get('left').get('score')
                right_score = item.get('right').get('score')
                logger.info(f'{live_time} | {game_time} | {left_score} - {right_score} | {user_chn} | {live_text}')

                img_url = item.get("img_url", '')
                if img_url:
                    logger.info(f'{img_url}')

            except Exception as e:
                logger.info('ERROR: Live Format Error.')
                continue

    def get_game_time(self, date, game_id):
        url = f"https://bifen4pc2.qiumibao.com/json/{date}/v2/{game_id}.htm?get={random.random()}"
        res = requests.get(url, headers=self.headers)
        game_info = res.json()
        game_time = game_info.get('period_cn', '')
        return game_time


if __name__ == '__main__':
    # h_obj = HupuSpider()
    # h_obj.home_page()
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    utc_today = datetime.now()
    beijing_today = utc_today.astimezone(shanghai_tz).strftime("%Y-%m-%d")
    z_obj = Zhiboba()
    z_obj.main(date=beijing_today, game_id='1415238', sid_no_change_limit=250)
