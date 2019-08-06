"""author : 杨文龙
"""
import re
import time
from lxml.etree import HTML
from random import choice
from qcc_spider.feach import FEACH
from common import get_proxy, get_log
from urllib import parse
# from  mongo import MongoDB
from easydict import EasyDict
import uuid
import pymongo
import execjs

DATABASE = pymongo.MongoClient("mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017")
DB = DATABASE["qixin_com"]["m6-new_results"]
log = get_log()

class QCC(object):
    def __init__(self):

        self.url = "https://www.qichacha.com/search_index?key={}&ajaxflag=1"

        self.f = FEACH()
        self.f.session.headers.update({
            "Connection": "keep-alive",
            # "Accept": "*/*",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            # "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "zh-CN,zh;q=0.9"
        })
        self.proxy = None

    # @staticmethod
    def get_pro(self):
        """
        获取代理
        :return:
        """
        proxy = choice(get_proxy(1))["ip"]
        self.proxy = {
            "http": "http://" + proxy,"https": "https://" + proxy,
        }

    def search_parmas(self,company_key):
        """
        搜索总共多少公司,返回详情页的url和后台认证的参数
        :return:
        """
        self.url = self.url.format(company_key)
        # self.f.session.headers.update({
        #     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        # })
        while 1:
            resp = self.f.get_req(self.url, proxies=self.proxy)
            if resp:
                etre = HTML(resp.text)
                info_parmas = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::*[1]/a/@onclick') #pc端
                info_URL = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::*[1]/a/@href')      #pc端

                return info_parmas, info_URL
            else:
                self.get_pro()

    def server_auth(self,data,company_info_url):
        """
        访问服务器进行后台认证,认证通过返回详情url,并替换refer
        :return:
        """
        count = 0
        while 1:
            resp = self.f.post_req(url="https://www.qichacha.com/search_addSearchIndex", data=data, proxies=self.proxy)

            if resp:
                refer_company_id = (company_info_url[6:]).split('.')[0]
                company_info_urls = "https://www.qichacha.com" + company_info_url
                return company_info_urls
            else:
                count += 1
                self.get_pro()
            if count > 5:
                return False

    def company_info_req(self,company_info_urls):
        """
        向详情页进行发起请求
        :return:
        """
        while 1:
            resp = self.f.get_req(url=company_info_urls,proxies=self.proxy)
            if resp:
                return resp
            else:
                self.get_pro()

    def company_info_parse(self,html_text,item,company_info_urls):
        """
        解析基本信息
        :param html_text:
        :param item:
        :return:
        """
        etre = HTML(html_text.text)
        clrq = "".join(etre.xpath('//*[contains(text(),"成立日期")]/following-sibling::*[1]/text()')).replace('\n', '').strip(' ')
        hzrq = "".join(etre.xpath('//*[contains(text(),"核准日期")]/following-sibling::*[1]/text()')).replace('\n','').strip(' ')
        zczb = "".join(etre.xpath('//*[contains(text(),"注册资本")]/following-sibling::*[1]/text()')).replace('\n','').strip(' ')
        # item["base"]["baseInfo"]["registerMoney"] = zczb
        # item["base"]["baseInfo"]["registerTime"] = clrq
        # item["base"]["baseInfo"]["confirmTime"] = hzrq

        DB.find_one_and_update({"_id":item["_id"]},{"$set":{"base.baseInfo.registerMoney":zczb,"base.baseInfo.registerTime":clrq,
                                                            "base.baseInfo.confirmTime":hzrq,"qcc_supplement":1}})


    def run(self):
        self.get_pro()

        count = DB.find({"qcc_supplement": 0}).count()
        cookie_count = 0
        while count:

            try:
                # mogodata = DB.find_one({"qcc_supplement": 0})
                company_key = "佳木斯益隆煤矿机械制造有限公司"
                # company_key = mogodata["companyName"]



                url  = "https://www.qichacha.com/gongsi_mindlist?type=his&viewType=1"

                resp = self.f.get_req(url=url, proxies=self.proxy)

                if resp != False:
                    time.sleep(1)
                    respcookie = resp.headers["Set-Cookie"]
                    updated = int(time.time()*1000)
                    sid = int(time.time()*1000)
                    info = int(time.time()*1000)
                    #
                    e = """function e() {
                             for (var e = 1 * new Date, t = 0; e == 1 * new Date; )
                                 t++;
                             return e.toString(16) + t.toString(16)
                        }"""

                    t = """
                        function t() {
                          return Math.random().toString(16).replace(".", "")
                        }
                    """
                    erx = execjs.get("Node").compile(e)
                    etx = execjs.get("Node").compile(t)

                    # UM_distinctid = erx.call("e") + "-" + etx.call("t") + "-" + "c343162" + "-" "1fa400" + "-" + erx.call("e")pc端
                    UM_distinctid = "UM_distinctid=" + erx.call("e") + "-" + etx.call("t") + "-" + "2d604637" + "-" "3d10d" + "-" + erx.call("e") + ";" #手机Iphone6
                    # zg_did = parse.quote(str({"sid":erx.call("e") + "-" + etx.call("t") + "-" + "c343162" + "-" "1fa400" + "-" + erx.call("e")})) pc端
                    zg_did = "zg_did=" + parse.quote(str({"sid":erx.call("e") + "-" + etx.call("t") + "-" + "2d604637" + "-" "3d10d" + "-" + erx.call("e")})) + ";"  #手机Iphone6

                    datas = {
                        "sid": sid,
                        "updated": updated,
                        "info": info,
                        "superProperty": "{}",
                        "platform": "{}",
                        "utm": "{}",
                        "referrerDomain": ""
                    }

                    # cookie = respcookie + ", zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=" + str(datas)
                    cookie = respcookie + ", zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=" + parse.quote(str(datas)) + ", " + UM_distinctid + ", " + zg_did

                    self.f.session.headers.update({
                        "Cookie": cookie,

                    })

                    info_parmas, company_infos = self.search_parmas(company_key)
                    # company_infos, company_url = self.search_parmas(company_key)
                    print("搜索页请求成功")
                    if company_infos != [] and info_parmas != []:

                        # item = mogodata

                        # for _ in range(len(company_infos)):
                        #     name = company_infos[_].replace("<em>","").replace("</em>","").replace(" ","")
                        #     company_info_urls = "https://m.qichacha.com" + company_url[_]
                        #     if name == company_key:
                        #         tml_text = self.company_info_req(company_info_urls)

                        #pc端
                        for _ in range(len(info_parmas)):

                            fol_result = (info_parmas[_].split("addSearchIndex")[1]).replace('(','').replace(')','').replace("'",'').replace(";",'')
                            if mogodata["companyName"] == fol_result.split(',')[0]:
                                fol_results = fol_result.split(',')
                                company_info_url = company_infos[_]

                                data = {
                                    "search_key":fol_results[0],
                                    "search_index":fol_results[1],
                                    "search_url":'',
                                    "company_name":fol_results[2],
                                    "type":fol_results[-1],
                                }

                                #基本信息
                                company_info_urls = self.server_auth(data,company_info_url)
                                html_text = self.company_info_req(company_info_urls)
                                self.company_info_parse(html_text,item,company_info_urls)

                        count -= 1

                    else:
                        self.get_pro()

            except:
                self.get_pro()










