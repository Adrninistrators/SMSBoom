#!/usr/bin/python python3
# coding=utf-8
'''
Author: whalefall
Date: 2021-08-07 14:15:50
LastEditTime: 2021-09-04 18:49:41
Description: 短信测压接口测试平台,测试200状态码的接口,不一定可用
'''
import time
from genericpath import exists
import os
import threading
import queue
from utils.db_sqlite import Sql
import re
import requests
import urllib3
import json
from pathlib import Path
urllib3.disable_warnings()
websize_json_path = str(
    Path(__file__).resolve().parent.joinpath('hzWebSize.json'))


class SMS(object):
    # 默认的请求密钥
    default_phone = "15019682928"
    key_default = f"?hm={default_phone}&ok="

    def __init__(self, website, key=key_default) -> None:
        if website == None:
            return
        self.url = website
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36",
        }
        if key == '' or key == None:
            self.key = SMS.key_default
        else:
            self.key = key
        self.api_queue = queue.Queue()
        self.db = Sql()
        self.lock = threading.Lock()

    def get_sms_api(self):
        '''请求短信轰炸平台'''
        with requests.session() as ses:
            ses.get(self.url, headers=self.header, verify=False)
            resp = ses.get(f"{self.url}{self.key}", headers=self.header)
        # print(resp.text)
        pat = re.compile(r"<img src='(.*?)' alt=''/>")
        apis = pat.findall(resp.text)
        assert not apis == [], f"网站{self.url}{self.key}未找到任何接口!"
        print(f"网站{self.url}{self.key}获取到的原始接口总数:%s" % (len(apis)))
        # 需要进行预处理

        for api in apis:

            # 三重校验网址
            # 排除接口中没有电话号码的网址
            if SMS.default_phone not in api:
                continue

            # 去除空白字符并替换默认手机号
            api = api.strip().replace(" ", "").replace(
                SMS.default_phone, "{phone}")

            # 校验网址开头
            if not (api.startswith("https://") or api.startswith("http://")):
                continue

            self.api_queue.put(api)
        print(f"网站{self.url}{self.key}Put到队列的接口总数:%s" %
              (self.api_queue.qsize()))

    def check_theads(self):
        '''多线程检查可用性'''
        while True:
            if self.api_queue.empty():
                print(f"线程{threading.current_thread().name}结束")
                break
            api = self.api_queue.get()

            try:
                with requests.get(api.replace("{phone}", SMS.default_phone), headers=self.header, timeout=10, verify=False) as resp:
                    if resp.status_code == 200:
                        print(
                            f'[SUC]校验成功!队列数:{str(self.api_queue.qsize())}')
                        with self.lock:
                            # 多线程写sqlite数据库要加锁
                            r = self.db.update(api)
                            if r:
                                print(
                                    f"[Good]已添加{api} 队列数:{str(self.api_queue.qsize())}")
            except Exception as e:
                print(
                    f"[ERROR]请求接口出错 队列数:{str(self.api_queue.qsize())}")
                pass
            finally:
                self.api_queue.task_done()

    def main(self):
        self.get_sms_api()
        # 在此设置线程数 int 类型
        threads_count = 128
        threads = [
            threading.Thread(target=self.check_theads, name=f"Theads-{i}")
            for i in range(1, threads_count+1)
        ]
        for thread in threads:
            thread.start()
            # thread.join()
            
        self.api_queue.join()
            


def readJson():
    '''读取网站json文件,返回一个迭代器'''
    assert os.path.exists(
        websize_json_path), "轰炸网站json文件未找到,请按格式新建一个hzWebSize.json文件"
    with open(websize_json_path, mode='r', encoding='utf-8') as f:
        j = f.read()

    try:
        js = json.loads(j)
    except Exception as e:
        print(f'解析hzWebSize.json文件错误,{e}')
        raise e

    for data in js:
        yield data


if __name__ == '__main__':
    # 轰炸平台
    # # 实例: http://hz.7qi.me/index.php?0pcall={SMS.default_phone}&ok=
    # # https://hz.79g.cn/index.php?0pcall=15019682928&ok=
    # url = "https://hz.79g.cn/index.php"
    # # 0pcall=15019682928&c=1 需要加f格式化字符串！！
    # spider = SMS(url, key=f'?0pcall={SMS.default_phone}&ok=')
    # # url = 'https://120.77.244.209/sdlz/yh.php'
    # # spider = SMS(url)
    # spider.main()

    assert os.path.exists(
        websize_json_path), "轰炸网站json文件未找到,请按格式新建一个hzWebSize.json文件"

    for websize in readJson():
        print(f"网站{websize}开始!")
        try:
            s = time.time()
            spider = SMS(websize.get('url', None), key=websize.get(
                'key', None).replace('{SMS.default_phone}', SMS.default_phone))
            spider.main()
            b = time.time()
        except Exception as e:
            print(f'[ERROR]发生错误{e}')
        print(f'网站{websize}结束! 耗时:{b-s}s')
