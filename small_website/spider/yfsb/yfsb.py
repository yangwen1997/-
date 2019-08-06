#! /uer/bin/env  python
#  coding: utf-8
'''
@author: 杨文龙
@contact:  yangwenlong@dgg.net
@file : cdgk.py
@time: 2019/5/20
@desc:
'''



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
DATABASE = 'gateways_news'
collection = 'tzw_result'
DB = MongoDB(uri=URI, db=DATABASE, collection=collection)

#获取全局日志
log = get_log()


#本地redis
red_cli = REDIS


class TZLT(object):

    def __init__(self,proxy):
        self.url = 'http://www.tz1288.com/yellowpages.html'
        self.proxy = proxy
        self.feach = FEACH()

    def gate(self):
        """
        类别
        :return:
        """
        resp = self.feach.get_req(url=self.url, proxies=self.proxy)
        etre = HTML(resp)
        category_list = etre.xpath('//li[@class=" industryGroup"]/p/text()')

        for _ in range(len(category_list)):
            item = EasyDict()
            index = category_list[_]
            item.category = index

            lt = []
            category_lt = etre.xpath('//div[@id="industryGroup-{}"]//dd/a/@href'.format(_))
            for x in category_lt:
                url = 'http://www.tz1288.com' + x
                lt.append(url)
            item.url_list = lt
            # print(item)
            red_cli.sadd('tz_category',str(item))


    def dq(self):
        """
        省份
        :return:
        """

        count = red_cli.scard('tz_category')
        while count:

            #没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            data_category = red_cli.srandmember('tz_category')
            cate = eval(data_category)["category"]
            url_list = eval(data_category)["url_list"]
            tag = 0
            for _ in url_list:
                item = EasyDict()
                item.category = cate
                resp = self.feach.get_req(url=_, proxies=proxy)
                if resp != False:
                    tree = HTML(resp)
                    dq_names = tree.xpath('//div[@class="Yellowpages"]//div[2]/div[2]//ul/li/a/text()')
                    dq_urls = tree.xpath('//div[@class="Yellowpages"]//div[2]/div[2]//ul/li/a/@href')
                    lt = []
                    for _ in range(0, len(dq_names)):
                        its = EasyDict()
                        if dq_names[_] == '不限':
                            continue
                        else:
                            its.dq_name = dq_names[_]
                            its.dq_urls = 'http://www.tz1288.com' + dq_urls[_]
                            lt.append(its)
                    item.dq = lt
                    red_cli.sadd('tz_dq', str(item))
                    pprint('数据插入成功')
                else:
                    tag = 1
                    break

            if tag == 1:
                print('请求失败')
                pass
            else:
                pprint('数据插入redis全部成功')
                red_cli.srem('tz_category', data_category)
                count -= 1

    def city(self):
        """
        城市
        :return:
        """
        count = red_cli.scard('tz_dq')
        while count:

            #没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            data_category = red_cli.srandmember('tz_dq')
            cate = eval(data_category)["category"]
            url_list = eval(data_category)["dq"]
            tag = 0

            for _ in url_list:
                item = EasyDict()

                item.category = cate
                item.dq_name = _["dq_name"]
                durl = _["dq_urls"]
                resp = self.feach.get_req(url=durl,proxies=proxy)
                if resp != False:
                    tree = HTML(resp)
                    city_name = tree.xpath('//div[@class="Yellowpages"]//div[2]/div[3]//ul/li/a/text()')
                    city_urls = tree.xpath('//div[@class="Yellowpages"]//div[2]/div[3]//ul/li/a/@href')

                    lt = []
                    for x in range(0,len(city_urls)):
                        city_items = EasyDict()

                        if city_name[x] == '不限':
                            continue
                        else:
                            city_items.city = city_name[x]
                            city_items.city_url = 'http://www.tz1288.com' + city_urls[x]
                            lt.append(city_items)
                    item._city = lt

                    red_cli.sadd('city_list', str(item))
                    print('插入的数据为{}'.format(item))
                else:
                     break

            if tag == 1:
                print('请求失败')
                pass
            else:
                pprint('数据插入redis全部成功')
                red_cli.srem('tz_dq', data_category)
                count -= 1

    def page(self,item,resp,proxy):
        """
        分页
        :param item:
        :param resp:
        :param proxy:
        :return:
        """
        TAG = 1
        page = re.findall(r'span class="pageNum">共(\d+)页 第\d+页</span>',resp)
        if page != []:
            page = ''.join(page)
            stat = str(1)
            if page != stat or page != 1:
                for _ in range(2,(int(page) + 1)):
                    url = 'http://www.tz1288.com/c/a0b32c3608f.html?p={}'.format(_)
                    response = self.feach.get_req(url, proxies=proxy)
                    if response != False:
                        etre = HTML(resp)
                        url_lt = etre.xpath('//div[@class="corpinfo"]//h3/a/@href')
                        for x in url_lt:
                            item.info_url = x
                            red_cli.sadd('info_list', str(item))
                            log.info('存储的数据为--{}'.format(item))

                    else:
                        TAG = 3
                        break
            if TAG == 3:
                return False
            else:
                pass
    def data_url(self):
        """
        每页中的详情页的url
        :return:
        """
        count = red_cli.scard('city_list')
        while count:

            #没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            url_list = red_cli.srandmember('city_list')
            category = eval(url_list)["category"]
            dq_name = eval(url_list)["dq_name"]
            _city = eval(url_list)["_city"]

            TAG = 1
            if _city != []:
                for _ in _city:
                    item = EasyDict()

                    item.category = category
                    item.dq_name = dq_name
                    item.city = _["city"]
                    city_url = _["city_url"]
                    resp = self.feach.get_req(city_url,proxies=proxy)
                    if resp != False:
                        etre = HTML(resp)
                        url_lt = etre.xpath('//div[@class="corpinfo"]//h3/a/@href')
                        for x in url_lt:
                            item.info_url = x
                            red_cli.sadd('info_list', str(item))
                            log.info('抓取的数据为{}'.format(item))

                        #抓取分页
                        page_stats = self.page(item, resp,proxy)
                        if page_stats == False:
                            break

                    else:
                        TAG = 2
                        break

                #如果异常退出不删除redis中的数据
                if TAG == 2:
                    pass
                else:
                    log.info('按照地区分类当前页面所有详情url抓取完毕')
                    red_cli.srem('city_list', url_list)
                    count -= 1

            else:
                continue

    def data_info(self):
        """
        抓取详情页里面的内容
        :return:
        """
        count = red_cli.scard('info_list')
        while count:
            #没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            info_data = red_cli.srandmember('info_list')

            item = EasyDict()

            # 分类，省份，城市，网页url,来源网站，标志符
            item.companyIndustry = eval(info_data)["category"]
            item.companyProvince = eval(info_data)["dq_name"]
            item.companyCity = eval(info_data)["city"]
            item.companyUrl = eval(info_data)["info_url"]
            item.websource = 'http://www.tz1288.com/yellowpages.html'
            item.flag = None
            resp = self.feach.get_req(url=item.companyUrl ,proxies=proxy)
            if resp != False:
                etre = HTML(resp)

                #out_names：联系人，companyAddr：公司地址，imTel：座机
                try:
                    item.companyName = etre.xpath('//dt[@class="c333 fs14"]/text()')[0]
                    item._id = hashlib.md5(str(item.companyName).encode('utf-8')).hexdigest()
                    out_names = etre.xpath('//div[@class="com-pro Mainsideline mb15"]//span[@class="c-blue"]/text()')
                    if out_names != []:
                        item.outName = out_names[0]
                    else:
                        item.outName = ''

                    companyAddr = etre.xpath('//div[@class="com-pro Mainsideline mb15"]//tbody/tr[7]/td[last()]/text()')
                    if companyAddr != []:
                        item.companyAddr = companyAddr[0]
                    else:
                        item.companyAddr = ''

                    imTel =  re.findall(r'电话：</span></td>\n<td>(.*?)</td>',resp)
                    if imTel != []:
                        item.imTel = [_ for _ in imTel]
                    else:
                        item.imTel = []

                    companyTel = re.findall(r'移动电话：</span></td>\n<td>([\d+]{11})</td>',resp)

                    if companyTel != []:
                        item.companyTel = [_ for _ in companyTel]
                    else:
                        item.companyTel = []
                    DB.mongo_add(item)
                    log.info('存储的数据为--{}'.format(item))
                    red_cli.srem('info_list',info_data)
                    count -= 1
                    gc.collect()

                except:
                    print('解析页面异常请查看错误页面url为{}'.format(item.companyUrl))
                    break

            else:
                pprint('请求网页失败尝试重试')
                pass

    def run(self):
        """
        开始函数
        :return:
        """
        # self.gate()
        # self.dq()
        # self.city()
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
    # proxy = 'https://{}'.format(proxy)

    tz = TZLT(proxy)
    tz.run()



def pro():
    """
    使用进程
    :return:
    """

    #开启的进程个数
    pool = multiprocessing.Pool(processes=8)

    for i in range(4):
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