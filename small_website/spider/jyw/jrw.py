#! /uer/bin/env  python
#  coding: utf-8
'''
@author: 杨文龙
@contact:  yangwenlong@dgg.net
@file : jrw.py
@time: 2019/6/4
@desc:
'''

from spider.feach import FEACH
from spider.common import get_proxy,get_log,REDIS
from spider.mongo import MongoDB

import threadpool
import asyncio
import multiprocessing

import gc
import hashlib
import redis
import time
import string
import re
from pprint import pprint
from easydict import EasyDict
from lxml.etree import HTML
from random import choice

#mongodb 连接
URI = 'mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017'
# URI = 'mongodb://127.0.0.1:27017'
DATABASE = 'yangwl'
collection = 'jrw_result'
DB = MongoDB(uri=URI, db=DATABASE, collection=collection)

#获取全局日志
log = get_log()


#本地redis
red_cli = REDIS


class TZLT(object):

    def __init__(self,proxy):
        self.url = 'https://www.jvrong.com/?location=sell'
        self.proxy = proxy
        self.feach = FEACH()

    def gate(self):
        """
        类别 : 省份
        :return:
        """
        resp = self.feach.get_req(url=self.url)
        if resp:
            etre = HTML(resp)
            category_urls = etre.xpath('//table/tr/th/a/@href')
            category_names = etre.xpath('//table/tr/th/a/text()')

            for _ in range(len(category_urls)):
                item = EasyDict()
                item.category_url = "https://www.jvrong.com" + str(category_urls[_])
                item.category_name = category_names[_]
                red_cli.sadd('jr_category',str(item))

    def city(self):
        """
        城市
        :return:
        """
        count = red_cli.scard('jr_category')
        while count:

            #没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            data_category = red_cli.srandmember('jr_category')
            cate = eval(data_category)["category_name"]
            cate_url = eval(data_category)["category_url"]
            tag = 0

            item = EasyDict()
            item.category = cate
            resp = self.feach.get_req(url=cate_url,proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                city_urls = etre.xpath('//div[@class="filter-item"]/div[last()]/a/@href')
                city_names = etre.xpath('//div[@class="filter-item"]/div[last()]/a/text()')

                for _ in range(len(city_names)):
                    if city_names[_] == "全部":
                        continue
                    else:
                        item.city_url = "https://www.jvrong.com"  + str(city_urls[_])
                        item.city_name = city_names[_]
                        red_cli.sadd('jr_city', str(item))
            else:
                tag = 1

            if tag == 1:
                print('请求失败')
                pass
            else:
                pprint('数据插入redis全部成功')
                red_cli.srem('jr_category', data_category)
                count -= 1

    def hygate(self):
        """
        行业，分类
        :return:
        """
        count = red_cli.scard('jr_city')
        while count:

            # 没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            data_category = red_cli.srandmember('jr_city')
            province = eval(data_category)["category"]
            city = eval(data_category)["city_name"]
            city_url = eval(data_category)["city_url"]
            tag = 0

            item = EasyDict()
            item.province = province
            item.city = city
            resp = self.feach.get_req(url=city_url, proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                hygate_urls = etre.xpath('//div[@id="sidebar"]/div/div/div//a/@href')
                hygate_names = etre.xpath('//div[@id="sidebar"]/div/div/div//a/text()')

                for _ in range(len(hygate_names)):
                    if hygate_names[_] == "全部":
                        continue
                    else:
                        item.city_url = "https://www.jvrong.com" + str(hygate_urls[_])
                        item.city_name = hygate_names[_]
                        red_cli.sadd('jr_hycate', str(item))
                        log.info("数据插入成功{}".format(item))
            else:
                tag = 1

            if tag == 1:
                print('请求失败')
                pass
            else:
                pprint('数据插入redis全部成功')
                red_cli.srem('jr_city', data_category)
                count -= 1

    def page(self,item,city_url,proxy):
        """
        分页
        :param item:
        :param resp:
        :param proxy:
        :return:
        """
        page_num = 2
        city_url = city_url.replace(".htm", "_{}.htm".format(page_num))
        while 1:

            resp = self.feach.get_req(url=city_url,proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                hygate_urls = etre.xpath('//div[@class="list-item-content"]/div[1]/a/@href')
                hygate_names = etre.xpath('//div[@class="list-item-content"]/div[1]/a/text()')
                if len(hygate_urls) == 30:
                    for _ in range(len(hygate_names)):
                        item.company_url = hygate_urls[_]
                        item.company_name = hygate_names[_]
                        red_cli.sadd('jr_info_url', str(item))
                    page_num += 1
                    if page_num > 100:
                        break
                    else:
                        city_url = city_url.replace("{}.htm".format(page_num - 1), "{}.htm".format(page_num))

                else:
                    for _ in range(len(hygate_names)):
                        item.company_url = hygate_urls[_]
                        item.company_name = hygate_names[_]
                        red_cli.sadd('jr_info_url', str(item))
                    break
            else:
                proxy = choice(get_proxy())["ip"]
                proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

    def data_url(self):
        """
        每页中的详情页的url
        :return:
        """
        count = red_cli.scard('jr_hycate')
        while count:

            #没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            data_category = red_cli.srandmember('jr_hycate')
            item = EasyDict()
            item.province = eval(data_category)["province"]
            item.city = eval(data_category)["city"]
            item.category_name = eval(data_category)["city_name"]
            city_url = eval(data_category)["city_url"]

            resp = self.feach.get_req(url=city_url, proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                hygate_urls = etre.xpath('//div[@class="list-item-content"]/div[1]/a/@href')
                hygate_names = etre.xpath('//div[@class="list-item-content"]/div[1]/a/text()')
                tag = 0
                if len(hygate_urls) >= 1:
                    for _ in range(len(hygate_names)):
                        item.company_url = hygate_urls[_]
                        item.company_name = hygate_names[_]
                        red_cli.sadd('jr_info_url',str(item))
                    if len(hygate_urls) >= 30:
                        self.page(item,city_url,proxy)

                else:
                    log.info("该城市分类暂未数据")
            else:
                tag = 1

            if tag == 1:
                print('请求失败')
                pass
            else:
                pprint('数据插入redis全部成功')
                red_cli.srem('jr_hycate', data_category)
                count -= 1

    def data_info(self):
        """
        抓取详情页里面的内容
        :return:
        """
        count = red_cli.scard('jr_info_url')
        while count:

            tag = 0
            #过滤redis中的假的url
            info_data = red_cli.srandmember('jr_info_url')
            url = 'https://www.jvrong.com' + str(eval(info_data)["company_url"])
            judge = url[-4:]

            if judge != '.htm':

                red_cli.srem('jr_info_url',info_data)
                log.info("该网站不正确，删除这条数据sucess.....")
                count -= 1

            else:
                # 没爬取一次分类换一个IP
                proxy = choice(get_proxy())["ip"]
                proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

                resp = self.feach.get_req(url=url,proxies=proxy)
                if resp != False:
                    item = EasyDict()
                    etre = HTML(resp)
                    try:
                        item.companyName = "".join(etre.xpath('//tbody[@id="meta-table"]/tr[1]/td[last()]/a/text()'))
                        item._id = hashlib.md5(str(item.companyName).encode(encoding='utf-8')).hexdigest()
                        item.outName = "".join(etre.xpath('//tbody[@id="meta-table"]/tr[2]/td[last()]/text()'))
                        item.companyUrl = url
                        item.companyCity = eval(info_data)["city"]
                        item.companyProvince = eval(info_data)["province"]
                        item.companyIndustry =eval(info_data)["category_name"]
                        item.websource = "https://www.jvrong.com/"
                        item.flag = None

                        #地址/电话/座机号 单独处理
                        companyAddr = etre.xpath('//tbody[@id="meta-table"]/tr[3]/td[last()]//text()')
                        item.companyAddr = companyAddr[4].replace('\r','').replace('\t','').replace('\n','')

                        #扫描整个字符串是否是座机号
                        companyTels = etre.xpath('//tbody[@id="meta-table"]/tr[last()]/td[last()]/p/strong[2]/text()')
                        imTel = []
                        companyTel = []
                        if companyTels != []:
                            for _ in companyTels:
                                result = re.search('-',_)
                                if result:
                                    imTel.append(_)
                                else:
                                    if _[0] == '0' or _[0] == '4':
                                        imTel.append(_)
                                    companyTel.append(_)
                        imTels = etre.xpath('//tbody[@id="meta-table"]/tr[last()]/td[last()]/p/strong[1]/text()')

                        if imTels != []:
                            for _ in imTels:
                                result = re.search('-', _)
                                if result:
                                    imTel.append(_)
                                else:
                                    if _[0] == '0' or _[0] == '4':
                                        imTel.append(_)
                                    companyTel.append(_)
                        item.imTel = imTel
                        item.companyTel = companyTel

                        DB.mongo_add(item)
                        tag = 1
                        log.info("数据存储成功-{}".format(item))
                    except:
                        log.info('解析异常，请查看url--{}'.format(item.companyUrl))
                        tag = 0

                else:
                    log.info("请求超时")

                if tag == 1:
                    red_cli.srem('jr_info_url',info_data)
                    print('删除redis中该条详情url成功')
                    count -= 1


    def run(self):
        """
        开始函数
        :return:
        """
        # self.gate()
        # self.city()
        # self.hygate()
        # self.data_url()
        self.data_info()



def func(*args):
    """
    爬取准备
    :param args:
    :return:
    """

    #获取代理IP
    # proxy = choice(get_proxy())["ip"]
    # proxy ={'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}
    proxy = '127.0.0.1'

    tz = TZLT(proxy)
    tz.run()

def pro():
    """
    使用进程
    :return:
    """

    #开启的进程个数
    pool = multiprocessing.Pool(processes=11)

    for i in range(10):
        pool.apply_async(func)

    pool.close()
    pool.join()

def thr():
    """
    使用线程
    :return:
    """
    pool = threadpool.ThreadPool(10)
    name_list = ['1','2','3','4','5','6']
    res = threadpool.makeRequests(func,name_list)
    [pool.putRequest(req) for req in res]
    pool.wait()

def main():
    """
    程序入口函数
    :return:
    """
    pro()
    # thr()


if __name__ == '__main__':
    main()