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
import cpca
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
collection = 'w1_114_result'
DB = MongoDB(uri=URI, db=DATABASE, collection=collection)

#获取全局日志
log = get_log()


#本地redis
red_cli = REDIS


class SNW(object):

    def __init__(self,proxy):
        self.url = 'http://corp.net114.com/'
        self.proxy = proxy
        self.feach = FEACH()

    def gate(self):
        """
        类别 : 行业分类
        :return:
        """
        resp = self.feach.get_req(url=self.url)
        if resp:
            etre = HTML(resp)

            category_names = etre.xpath('//div[@class="row"]/div[@class="center-bg"]')

            for _ in range(len(category_names)):
                item = EasyDict()
                item.category_name = category_names[_].xpath('.//div[1]/h3/text()')[0].strip(' ')
                ul_list = category_names[_].xpath('.//ul[@class="enterprise-text-li"]/li/p/a/@href')
                for x in ul_list:
                    item.urls = str(x)
                    red_cli.sadd('wl_114_category',str(item))
                    log.info("存入redis成功--{}".format(item))

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
        city_url = city_url.replace(".htm", "-p-{}.htm".format(page_num))
        while 1:

            resp = self.feach.get_req(url=city_url,proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                hygate_urls = etre.xpath('//div/self::div[@class="enter-title"]/h1/a/@href')

                if len(hygate_urls) >= 20:
                    for _ in range(len(hygate_urls)):
                        item.company_url = hygate_urls[_]
                        red_cli.sadd('wl_114_info_url', str(item))

                    log.info("第{}页抓取完毕".format(page_num))
                    page_num += 1
                    if page_num > 100:
                        break
                    else:
                        city_url = city_url.replace("{}.htm".format(page_num - 1), "{}.htm".format(page_num))

                else:
                    for _ in range(len(hygate_urls)):
                        item.company_url = hygate_urls[_]
                        red_cli.sadd('wl_114_info_url', str(item))
                        log.info("该类别抓取完毕")
                    break
            else:
                log.info("抓取分页过程中代理失效更换代理")
                proxy = choice(get_proxy())["ip"]
                proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

    def data_url(self):
        """
        每页中的详情页的url
        :return:
        """
        count = red_cli.scard('wl_114_category')
        while count:

            #没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            data_category = red_cli.srandmember('wl_114_category')
            item = EasyDict()
            item.category_name = eval(data_category)["category_name"]
            city_url = eval(data_category)["urls"]

            resp = self.feach.get_req(url=city_url, proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                hygate_urls = etre.xpath('//div/self::div[@class="enter-title"]/h1/a/@href')
                tag = 0
                if len(hygate_urls) >= 1:
                    for _ in range(len(hygate_urls)):
                        item.company_url = hygate_urls[_]
                        red_cli.sadd('wl_114_info_url',str(item))
                        log.info("首页数据-{}-存入redis完成".format(item))
                    log.info("初始页面公司数据url抓取完毕，准备抓取分页")
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
                red_cli.srem('wl_114_category', data_category)
                count -= 1

    def data_info(self):
        """
        抓取详情页里面的内容
        :return:
        """
        count = red_cli.scard('wl_114_info_url')
        while count:

            try:
                tag = 0
                #过滤redis中的假的url
                info_data = red_cli.srandmember('wl_114_info_url')
                category_name = eval(info_data)["category_name"]
                url = eval(info_data)["company_url"]


                # 没爬取一次分类换一个IP
                proxy = choice(get_proxy())["ip"]
                proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

                resp = self.feach.get_req(url=url,proxies=proxy)
                if resp != False:
                    item = EasyDict()
                    etre = HTML(resp)
                    try:
                        companyName_pat = re.compile(r'<div class="top_text_title">(.*?)</div>|<dl class="infobox-title"><dt><h1>(.*?)</h1>', re.M)
                        for _ in re.findall(companyName_pat,resp):
                            for x in _:
                                if x:
                                    item.companyName = x
                        item._id = hashlib.md5(str(item.companyName).encode(encoding='utf-8')).hexdigest()

                        outName_pat = re.compile(r'</span>(.*?)</dd><dd  ><span>联系电话|<p>联系人：(.*?) （市场部经理）</p>')
                        for outNames in re.findall(outName_pat,resp):
                            for outName in outNames:
                                if outName:
                                    item.outName = outName


                        item.companyUrl = url
                        Addr_pat = re.compile(r'<p>地  址：(.*?)</p>|<span>详细地址：</span>(.*?)</dd>')
                        for companyAddrs in re.findall(Addr_pat,resp):
                            for companyAddr in companyAddrs:
                                if companyAddr:
                                    item.companyAddr = companyAddr

                        if item.companyAddr:
                            try:
                                result = cpca.transform([item.companyAddr])
                                item.companyProvince = result["省"][0]
                                item.companyCity = result["市"][0]
                            except:
                                item.companyProvince = ''
                                item.companyCity = ''

                        item.companyIndustry =eval(info_data)["category_name"]
                        item.websource = "http://corp.net114.com/"
                        item.flag = None

                        imTel = []
                        companyTel = []
                        phone = etre.xpath('//span[contains(text(),"联系电话")]/ancestor::dd/text()')
                        if phone == []:
                            phone = etre.xpath('//font[contains(text(),"电话")]/text()')
                            if phone != []:
                                phone = re.findall(r'电话：(.*?)',phone[0])

                        if int(phone[0][0]) != 1:
                            imTel.append(phone[0])
                        else:
                            companyTel.append(phone[0])

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
                    red_cli.srem('wl_114_info_url',info_data)
                    print('删除redis中该条详情url成功')
                    count -= 1
            except:

                log.info('页面错误，请查看规则{}'.format(url))



    def run(self):
        """
        开始函数
        :return:
        """
        # self.gate()
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

    tz = SNW(proxy)
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