#! /uer/bin/env  python
#  coding: utf-8
'''
@author: 杨文龙
@contact:  yangwenlong@dgg.net
@file : cdgk.py
@time: 2019/5/20
@desc:
'''

import redis
from pprint import pprint
import requests
from fake_useragent import UserAgent
#本地redis
red_cli = redis.Redis(host='127.0.0.1',port=6379)

ua = UserAgent()


class FEACH(object):

    def __init__(self):
        self.session = requests.session()
        headers = headers = {
            'User-Agent' : ua.Chrome
        }
        self.session.headers.update(headers)

    def get_req(self, url:str=None, proxies=None):
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
            red_cli.sadd('bad_ip', str({"ip":proxies["http"]}))
            return False
        except IndexError as e:
            print(e)
        except ValueError as e:
            print(e)

