#! /uer/bin/env  python
#  coding: utf-8
'''
@author: 杨文龙
@contact:  yangwenlong@dgg.net
@file : cdgk.py
@time: 2019/5/20
@desc:
'''
import time

import redis
from pprint import pprint
import requests
# from fake_useragent import UserAgent
#本地redis
red_cli = redis.Redis(host='127.0.0.1',port=6379)

# ua = UserAgent()


class FEACH(object):

    def __init__(self):
        self.session = requests.session()
        headers = headers = {
            # 'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        }
        self.session.headers.update(headers)

    def get_req(self, url=None, proxies=None):
        """
        请求模块
        :param url:
        :param proxy:
        :return:
        """
        try:
            resp = self.session.get(url=url, proxies=proxies, timeout=10)
            if resp.status_code == 200:
                resp.encoding = resp.apparent_encoding
                return resp
            else:
                pprint('请求失败')
                return False

        except requests.exceptions.RequestException as e:
            print('请求超时代理ip--{}'.format(proxies))
            return False
        except IndexError as e:
            print(e)
        except ValueError as e:
            print(e)

    def post_req(self, url= None,data=None, proxies=None,):
        """
        请求模块
        :param url:
        :param proxy:
        :return:
        """
        try:
            resp = self.session.post(url=url, data=data,proxies=proxies, timeout=10)
            if resp.status_code == 200:
                resp.encoding = resp.apparent_encoding
                return resp
            else:
                pprint('请求失败')
                return False

        except requests.exceptions.RequestException as e:
            print('请求超时代理ip--{}'.format(proxies))
            return False
        except IndexError as e:
            print(e)
        except ValueError as e:
            print(e)