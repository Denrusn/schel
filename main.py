import requests
import random
import time


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

    def live(self, game_id="1231104", sid_no_change_limit=10):
        # 获取最大信号max_sid
        max_sid = self.get_live_max_sid(game_id)
        print(max_sid)

        # 往前查30个sid
        for i in range(max_sid - 30, max_sid + 1):
            live_data = self.get_live_data_by_sid(game_id, i)
            if not live_data:
                continue

            self.live_format(live_data)

        start_sid = max_sid
        sid_no_change = 0  # sid没变化情况计数
        while True:
            end_sid = self.get_live_max_sid(game_id)
            if end_sid > start_sid:
                for i in range(start_sid, end_sid + 1):
                    live_data = self.get_live_data_by_sid(game_id, i)
                    if not live_data:
                        continue
                    self.live_format(live_data)
                start_sid = end_sid
                sid_no_change = 0
            else:
                sid_no_change += 1
                time.sleep(2)

            if sid_no_change > sid_no_change_limit:
                # 如果sid没变化超过限制次数则退出循环
                print("SID No Change。。。")
                print("EXIT!")
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
    def live_format(data):
        for item in data:
            try:
                user_chn = item.get("user_chn")
                live_text = item.get("live_text")
                live_time = item.get("live_time")[11:]
                left_score = item.get('left').get('score')
                right_score = item.get('left').get('score')
                print(f"{live_time}| {left_score} - {right_score}| {user_chn}| {live_text}")

                img_url = item.get("img_url", '')
                if img_url:
                    print(img_url)

            except Exception as e:
                print('ERROR: Live Format Error.')
                continue


if __name__ == '__main__':
    # h_obj = HupuSpider()
    # h_obj.home_page()
    z_obj = Zhiboba()
    z_obj.live()
