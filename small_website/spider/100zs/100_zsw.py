#! /uer/bin/env  python
#  coding: utf-8
'''
@author: 杨文龙
@contact:  yangwenlong@dgg.net
@file : jrw.py
@time: 2019/6/11
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
collection = '100_zsw_result'
DB = MongoDB(uri=URI, db=DATABASE, collection=collection)

#获取全局日志
log = get_log()


#本地redis
red_cli = REDIS


class SNW(object):

    def __init__(self,proxy):
        self.url = 'http://www.zhaoshang100.com/qiye/'
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

            category_names = etre.xpath('//li/self::li[@class="mod_cate"]/h2/a/text()')
            category_urls = etre.xpath('//li/self::li[@class="mod_cate"]/h2/a/@href')

            for _ in range(len(category_names)):
                item = EasyDict()
                item.category_name = category_names[_]
                item.urls = 'http://www.zhaoshang100.com' + category_urls[_]
                red_cli.sadd('100_zsw_category',str(item))
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
        count = red_cli.scard('100_zsw_category')
        while count:

            # 没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            data_category = red_cli.srandmember('100_zsw_category')
            cate_names = eval(data_category)["category_name"]
            city_url = eval(data_category)["urls"]
            tag = 0

            item = EasyDict()
            item.category = cate_names
            resp = self.feach.get_req(url=city_url, proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                hygate_urls = etre.xpath('//ul/self::ul[@id="ul_i"]/li/a/@href')
                hygate_names = etre.xpath('//ul/self::ul[@id="ul_i"]/li/a/@title')

                for _ in range(len(hygate_names)):
                    if hygate_names[_] == "全部":
                        continue
                    else:
                        item.city_url = "http://www.zhaoshang100.com" + str(hygate_urls[_])
                        red_cli.sadd('category_urls', str(item))
                        log.info("数据插入成功{}".format(item))
            else:
                tag = 1

            if tag == 1:
                print('请求失败')
                pass
            else:
                pprint('数据插入redis全部成功')
                red_cli.srem('100_zsw_category', data_category)
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
        base_url = city_url
        city_url = base_url + str(page_num)
        company_md5 = ''
        while 1:

            resp = self.feach.get_req(url=city_url,proxies=proxy)
            if resp != False:
                etre = HTML(resp)
                hygate_urls = etre.xpath('//a/self::a[@class="proName02"]/@href')
                company_names = etre.xpath('//a/self::a[@class="proName02"]/text()')

                companys = hashlib.md5(str(company_names[0]).encode('utf-8')).hexdigest()
                if companys != company_md5:
                    for _ in range(len(hygate_urls)):
                        item.company_url = "http://www.zhaoshang100.com" + hygate_urls[_]
                        item.company_name = company_names[_]
                        company_md5 = hashlib.md5(str(company_names[0]).encode('utf-8')).hexdigest()
                        red_cli.sadd('100_zsw_info_url',str(item))

                    page_num += 1
                    city_url = base_url + str(page_num)
                    log.info('第{}页数据存储完毕'.format(page_num - 1))

                else:
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
        count = red_cli.scard('category_urls')
        while count:

            try:
                #没爬取一次分类换一个IP
                proxy = choice(get_proxy())["ip"]
                proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

                data_category = red_cli.srandmember('category_urls')
                item = EasyDict()
                item.category_name = eval(data_category)["category"]
                city_url = eval(data_category)["city_url"]

                resp = self.feach.get_req(url=city_url, proxies=proxy)
                if resp != False:
                    etre = HTML(resp)
                    hygate_urls = etre.xpath('//a/self::a[@class="proName02"]/@href')
                    company_names = etre.xpath('//a/self::a[@class="proName02"]/text()')
                    tag = 0
                    if len(hygate_urls) >= 1:
                        for _ in range(len(hygate_urls)):
                            item.company_url = "http://www.zhaoshang100.com" + hygate_urls[_]
                            item.company_name = company_names[_]

                            red_cli.sadd('100_zsw_info_url',str(item))
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
                    red_cli.srem('category_urls', data_category)
                    count -= 1
            except:
                pass

    def data_info(self):
        """
        抓取详情页里面的内容
        :return:
        """
        count = red_cli.scard('100_zsw_info_url')
        while count:

            tag = 0
            #过滤redis中的假的url
            info_data = red_cli.srandmember('100_zsw_info_url')
            category_name = eval(info_data)["category_name"]
            url = eval(info_data)["company_url"]
            companynamse = eval(info_data)["company_name"]


            # 没爬取一次分类换一个IP
            proxy = choice(get_proxy())["ip"]
            proxy = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

            resp = self.feach.get_req(url=url,proxies=proxy)
            if resp != False:
                item = EasyDict()
                etre = HTML(resp)

                try:

                    item.companyName = companynamse
                    item._id = hashlib.md5(str(item.companyName).encode('utf-8')).hexdigest()
                    item.companyUrl = url
                    item.companyIndustry = category_name
                    item.websource = 'http://www.zhaoshang100.com/qiye/'
                    item.flag = None


                    #联系人
                    tag = 1
                    if tag == 1:
                        outName = etre.xpath('//i/self::i[contains(text(),"联系人")]/ancestor::li/text()')
                        if outName != []:
                            item.outName = outName[0]
                        else:
                            tag = 2
                    if tag == 2:
                        log.info('请查看页面规则-{}'.format(url))

                    # 地址
                    tag = 1
                    if tag == 1:
                        companyAddr = etre.xpath('//i/self::i[contains(text(),"公司地址")]/ancestor::li/text()')
                        if companyAddr != []:
                            item.companyAddr = companyAddr[0]
                        else:
                            tag = 2
                    if tag == 2:
                        log.info('请查看页面规则-{}'.format(url))

                    #联系电话
                    tag = 1

                    if tag == 1:
                        phone_tel = etre.xpath('//i/self::i[contains(text(),"联系电话")]/ancestor::li/text()')
                        if phone_tel != []:
                            if phone_tel[0][0] != '1':
                                item.imTel = [phone_tel[0]]
                            else:
                                item.companyTel = [phone_tel[0]]
                        else:
                            error_phone = etre.xpath('//i/self::i[contains(text(),"联系电话")]/ancestor::li/font/text()')
                            if error_phone:
                                if error_phone[0] == '未提交认证,系统隐藏联系方式,登陆后台提交即可恢复':
                                    red_cli.srem('100_zsw_info_url', info_data)
                                    print('删除redis中该条详情url成功')
                                    count -= 1
                                    item.imTel = []
                            else:
                                tag = 2
                    tag = 1

                    #手机号
                    companyTels = etre.xpath('//i/self::i[contains(text(),"联系手机")]/ancestor::li/text()')
                    if companyTels != []:
                        item.companyTel = [companyTels[0]]
                    else:
                        item.companyTel = []

                    #地址
                    if item.companyAddr:
                        try:
                            result = cpca.transform([item.companyAddr])
                            item.companyProvince = result["省"][0]
                            item.companyCity = result["市"][0]
                        except:
                            item.companyProvince = ''
                            item.companyCity = ''
                    if item.imTel == [] and item.companyTel == []:
                        tag = 1
                        log.info('没有手机号和座机号删除')
                    else:
                        tag = 1
                        DB.mongo_add(item)

                except:
                    etree = HTML(resp)
                    error = etree.xpath('////title/text()')[0]
                    if error == '100招商网 错误页面 404 Not Found':
                        red_cli.srem('wl_114_info_url', info_data)
                        print('错误页面，删除该数据{}'.format(eval(info_data)))
                        count -= 1
                    log.info('解析异常，请查看url--{}'.format(item.companyUrl))
                    tag = 0

            else:
                log.info("请求超时")

            if tag == 1:
                red_cli.srem('100_zsw_info_url',info_data)
                print('删除redis中该条详情url成功')
                count -= 1

    def run(self):
        """
        开始函数
        :return:
        """
        # self.gate()
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

    tz = SNW(proxy)
    tz.run()

def pro():
    """
    使用进程
    :return:
    """

    #开启的进程个数
    pool = multiprocessing.Pool(processes=16)

    for i in range(15):
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
    # pro()
    thr()


if __name__ == '__main__':
    main()