'''
@author     :   yangwenlong
@file       :   qcm_run
@explain    :   获取公司名录进行数据补充
@time       :   2019/9/12
@info       :   搜索公司如果没有数据回写mongo该条数据redis为2 如果存入成功回写mongo中该数据redis状态为10
'''
import asyncio
import aiohttp
import redis
import pymongo
import json
from commons import ABY_IP_,get_log,error_db
from lxml.etree import HTML
from easydict import EasyDict
from xpath_base import XPATH
from commons import db

#定义全局请求url
urls = "https://www.qichamao.com/search/all/{}?o=0&area=0&mfccode={}"

#log redis 实列化
log = get_log()
red = redis.Redis(host="127.0.0.1",port=6379,db=10)

DB = pymongo.MongoClient("mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017")
dbb = DB["all_com_wash"]["Guangdong"]

class QCM_spider(object):
    """
    企查猫爬虫类
    """
    def __init__(self,process):
        self.process = process

    def base_parse(self, result):
        """
        解析基本信息
        :return:
        """
        etree = HTML(result)
        url_lt = etree.xpath('//a[@class="listsec_tit"]/@href')
        if url_lt:
            url = "https://www.qichamao.com" + url_lt[0]
            return url

    async def get_req(self,session,url):
        """
        :param session:  aiohttp的session对象
        :param url:     请求的网址
        :return: 返回请求的文本信息
        """
        proxy = ABY_IP_()
        async with session.get(url, proxy=proxy["https"])as resp:
            result = await resp.text(encoding='utf-8')
            return result

    async def post_req(self,session,url,post_parmas):
        proxy = ABY_IP_()
        async with session.post(url,data=post_parmas, proxy=proxy["https"])as resp:
            result = await resp.text(encoding='utf-8')
            return result

    @staticmethod
    def result_filter(result:list):
        if result[0]:
            result = result[0].replace(" ","").replace("\n","").replace("\t","").replace("\r","").replace("\x00","")
            return result
        result = ""
        return result

    @staticmethod
    def parse_base_info(response,item):
        """
        解析详情页中的工商基本数据
        :param response:
        :param item:
        :return:
        """
        while 1:
            try:
                etre = HTML(response)
                if not item.companyAddr:
                    item.companyAddr = "".join(etre.xpath('//div[@class="arthd_info"]/*[contains(text(),"企业地址")]/text()')).replace("企业地址：","")

                #解析基本信息
                base = EasyDict()
                qcm_xpath = XPATH()
                #邮箱  统一社会信用代码 注册号 机构代码 法定代表人 企业类型 经营状态 注册资本
                base.companyEmail = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.companyEmail) if etre.xpath(qcm_xpath.companyEmail)!= []])
                base.creditCode = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.creditCode) if etre.xpath(qcm_xpath.creditCode)])
                base.registerNum = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.registerNum) if etre.xpath(qcm_xpath.registerNum)])
                base.OrganizationCode = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.OrganizationCode) if etre.xpath(qcm_xpath.OrganizationCode)])
                base.legalMan = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.legalMan) if etre.xpath(qcm_xpath.legalMan)])
                base.companyType = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.companyType) if etre.xpath(qcm_xpath.companyType)])
                base.businessState = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.businessState) if etre.xpath(qcm_xpath.businessState)])
                base.registerMoney = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.registerMoney) if etre.xpath(qcm_xpath.registerMoney)])

                #成立日期  登记机关 经营期限 所属地区 核准日期 经营范围
                base.registerTime = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.registerTime) if etre.xpath(qcm_xpath.registerTime)])
                base.registOrgan = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.registOrgan) if etre.xpath(qcm_xpath.registOrgan)])
                base.operating_period = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.operating_period) if etre.xpath(qcm_xpath.operating_period)])
                base.area = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.area) if etre.xpath(qcm_xpath.area)!= []])
                base.approval_time = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.approval_time) if etre.xpath(qcm_xpath.approval_time)!= []])
                base.scope = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.scope) if etre.xpath(qcm_xpath.scope)!= []])
                item.base = base


                #变更信息
                changeInfo = EasyDict()
                changeInfo.changeInfoCount = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfoCount) if etre.xpath(qcm_xpath.changeInfoCount)!= []])
                changeInfo.changeInfo_project = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_project) if etre.xpath(qcm_xpath.changeInfo_project)!= []])
                changeInfo.changeInfo_after = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_after) if etre.xpath(qcm_xpath.changeInfo_after)!= []])
                changeInfo.changeInfo_end = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_end) if etre.xpath(qcm_xpath.changeInfo_end)!= []])
                changeInfo.changeInfo_time = QCM_spider.result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_time) if etre.xpath(qcm_xpath.changeInfo_time)!= []])
                item.changeInfo = changeInfo
                print(item)
                break
            except Exception as e:
                print(e)

    @staticmethod
    def item_copy_data(data):
        """
        获取mongo中原有数据添加到item字典
        :param item:
        :param data:
        """
        item = EasyDict()
        item.companyName = eval(data)["companyName"]
        item.outName = eval(data)["outName"]
        item.companyTel = eval(data)["companyTel"]
        item.companyUrl = eval(data)["companyUrl"]
        item.companyAddr = eval(data)["companyAddr"]
        item.companyCity = eval(data)["companyCity"]
        item.companyProvince = eval(data)["companyProvince"]
        return item

    async def run(self):
        data = red.srandmember("mfcode_name")

        mfcode = eval(data)["mfcode"]
        keys = eval(data)["companyName"]
        cookie = eval(data)["cookie"]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Cookie": cookie,
        }

        url = urls.format(keys, mfcode)
        async with aiohttp.ClientSession(headers=headers)as session:
            result = await self.get_req(session,url)
            info_url = self.base_parse(result)

            if info_url:
                response = await self.get_req(session,info_url)
                if response:
                    item = QCM_spider.item_copy_data(data)
                    QCM_spider.parse_base_info(response,item)
                    item._id = eval(data)["_id"]
                    item.qcm_url = info_url

                    #获取商标数量
                    orgCode = info_url.split("/")[-1].split(".")[0]
                    post_parmas = {
                        "orgCode": orgCode,
                        "page": "1",
                        "pagesize": "5",
                        "datacount": "0",
                    }
                    sb_result = await self.post_req(session,"https://www.qichamao.com/orgcompany/brandlistbycode",post_parmas)
                    res = json.loads(sb_result)
                    item.brandCount = res["rowCount"]

                    await db.mongo_add(item)
                    await dbb.find_one_and_update({"_id":item._id},{"$set":{"redis":10}})

                    log.info("数据回写到mongo中的redis为10")
                    red.srem("mfcode_name",data)

            else:
                #当搜索失败时逻辑
                log.info("解析的公司详情url为空，检测是否搜索到公司")
                etre = HTML(result)
                judge = "".join(etre.xpath('//em[@class="keyword SearchCompanyCount"]/text()'))
                if judge:
                    if judge == '0':
                        log.info('搜索到0家公司，回写Mongo中该数据的redis值为2')
                        _id = eval(data)["_id"]
                        await error_db.find_one_and_update({"_id":_id},{"$set":{"redis":2}})
                        red.srem("mfcode_name",data)
                else:
                    log.info('mfcode失效请重新获取名录')
                    data = eval(data)
                    del data["cookie"]
                    del data["mfcode"]
                    red.sadd("yyy",str(data))

async def task(x):
    """
    协程入口函数，并捕获异常失败自动重试，最多3次
    :param x:
    :return:
    """
    count = 1
    while True:
        try:
            start = QCM_spider(x)
            await start.run()

        except Exception as e:
            print(e)
            count += 1
        if count > 3:
            break

async def start():
    coroutine = [task(_) for _ in range(1,2)]
    tasks = [asyncio.ensure_future(_) for _ in coroutine]
    await asyncio.wait(tasks)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())

if __name__ == '__main__':
    main()