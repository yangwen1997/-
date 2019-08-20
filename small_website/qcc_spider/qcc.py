'''
author : 杨文龙
'''

import gc
import hashlib
import redis
import time
import string
import pymongo
import re
from pprint import pprint
from easydict import EasyDict
from lxml.etree import HTML
from random import choice
from qcc_spider.feach import FEACH
import json
from common import get_proxy, get_log
from urllib import parse
from city_category import cpca


#selenium库
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains, FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

log = get_log()

DATABASE = pymongo.MongoClient("mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017")
KEYS_DB = DATABASE["qcc_com"]["企查查最新融资表"]


class QCC(object):
    def __init__(self):
        # self.url = "https://www.qichacha.com/search?key=深圳市宏力捷电子有限公司"
        self.url = "https://www.qichacha.com/search?key="

        self.f = FEACH()
        self.f.session.headers.update({
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
        })
        self.proxy = None
        self.count = 1

    def chrome_driver(self):
        """
        实例化driver
        :return:
        """
        # 启动延时时间
        sleep_time = self.count*5
        log.info('延时{}s启动...'.format(sleep_time))
        # driver配置


        # chrome_options.add_argument("--incognito")
        # chrome_options.add_argument('--disable-extensions')
        # chrome_options.add_argument('--disable-infobars')
        # chrome_options.add_argument('-no-sandbox')
        # chrome_options.add_argument('--profile-directory=Default')
        # chrome_options.add_argument('--disable-plugins-discovery')
        # chrome_options.add_argument("--proxy-server=http://{}".format(ip))
        # chrome_options.add_argument("--proxy-server=127.0.0.1:8080")
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # 如果proxy_tag==1使用下面的配置方式，否则使用else下的配置方式


        # 实例化driver
        profile = FirefoxProfile()
        ## 第二步：开启“手动设置代理”
        profile.set_preference('network.proxy.type', 1)
        ## 第三步：设置代理IP
        profile.set_preference('network.proxy.http', '127.0.0.1')
        ## 第四步：设置代理端口，注意端口是int类型，不是字符串
        profile.set_preference('network.proxy.http_port', 8080)
        ## 第五步：设置htpps协议也使用该代理
        profile.set_preference('network.proxy.ssl', "127.0.0.1")
        profile.set_preference('network.proxy.ssl_port', 8080)




        # chrome_options.add_argument()
        self.driver = webdriver.Firefox(
            # chrome_options=chrome_options,
            profile,
            executable_path = "D:\software\FIREX_DEIVER\geckodriver.exe")
            # executable_path = "D:\software\chromedrive\chromedriver.exe")
        # 设置页面等待超时时间（由于代理网络有时延时较高，所以设置等待超时时间为40s）
        self.driver.set_page_load_timeout(40)

        return  self.driver

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
        self.url = self.url + company_key
        while 1:
            resp = self.f.get_req(self.url, proxies=self.proxy)
            if resp:
                etre = HTML(resp.text)
                info_parmas = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::td[1]/a/@onclick')
                info_URL = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::td[1]/a/@href')
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

        # 公司名称 唯一标识 手机 地址 省份 城市
        item.companyName = "".join(etre.xpath('//h1/text()'))
        item._id = hashlib.md5(str(item.companyName).encode('utf-8')).hexdigest()
        item.companyTel = []
        item.companyAddr = "".join(etre.xpath('//*[contains(text(),"企业地址")]/following-sibling::td/text()')).replace('\n','').strip(' ')

        if item.companyAddr:
            try:
                result = cpca.transform([item.companyAddr])
                item.companyProvince = result["省"][0]
                item.companyCity = result["市"][0]
            except:
                item.companyProvince = ''
                item.companyCity = ''

        # 网站上数据更新时间 经营状态 抓取时间 公司url 网站域名
        item.updateTime = "".join(etre.xpath('//p[@class="refs"]/@title')).replace('上次更新日期：','')
        item.businessState = "".join(etre.xpath('//*[contains(text(),"经营状态")]/following-sibling::td[1]/text()')).replace('\n','').strip(' ')
        item.collectTime = int((time.time()) * 1000)
        item.companyUrl = company_info_urls
        item.webSource = "https://www.qichacha.com"
        item.phone = "".join(etre.xpath('//*[contains(text(),"电话")]/following-sibling::*[1]/*/text()')).replace('\n','').strip(' ')

        # 股东信息
        holderInfo = []
        holderInfos = etre.xpath('/html/body/div[3]/div/div/div[2]/section[@id="partnerslist"]/table/tr[1]/following-sibling::tr')
        holderInfo_count = len(holderInfos)
        if len(holderInfos) > 1:
            for _ in holderInfos:
                holderInfo_item = EasyDict()
                holderInfo_item.hiName = "".join(_.xpath('.//div[contains(@class,"m-t-xs ptag")]/preceding::a/h3/text()'))
                holderInfo_item.hiRatio = "".join(_.xpath('.//td[@class="text-center"][1]/text()')).replace(" ","").replace("\n","")
                holderInfo_item.hiContribu = "".join(_.xpath('.//td[@class="text-center"][2]/text()')).replace(" ","").replace("\n","")
                holderInfo_item.hiContribu_time = "".join(_.xpath('.//td[@class="text-center"][3]/text()')).replace(" ","").replace("\n","")
                holderInfo.append(holderInfo_item)
        else:
            pass

        #股东职位信息
        employeeInfo = []
        employeeInfos = etre.xpath('/html/body/div[3]/div/div/div[2]/section[@id="partnerslist"]/table/tr[1]/following-sibling::tr')
        employeeInfo_count = len(employeeInfos)

        if len(employeeInfos) > 1:
            for _ in employeeInfos:
                employeeInfoitem = EasyDict()
                employeeInfoitem.scPosition = "".join(_.xpath('.//div[@class="m-t-xs ptag"]//text()'))
                employeeInfoitem.scName = "".join(_.xpath('.//h3[@class="seo font-14"]/text()'))
                employeeInfo.append(employeeInfoitem)
        else:
            pass

        #分支机构
        branchInfo = []
        branchInfos = etre.xpath('/html/body/div[3]/div/div/div[2]/section[@id="branchelist"]/table/tr[1]/following-sibling::tr')

        branchInfo_count = len(branchInfo)
        if len(branchInfos) > 1:
            for _ in branchInfos:
                branchInfoitem = EasyDict()
                branchInfoitem.bCompanyName = "".join(_.xpath('.//td[2]//a//text()')).replace("\n","").replace(" ","")
                branchInfoitem.bName = "".join(_.xpath('.//td[3]//a/h3/text()'))


                branchInfo.append(branchInfoitem)
        else:
            pass

        #变更信息
        changeInfo = []
        changeInfos = etre.xpath('/html/body/div[3]/div/div/div[2]/section[@id="Changelist"]//div[@id="ChangelistTable"]/table/tr')

        changeInfo_count = len(changeInfos)
        if len(changeInfos) > 1:
            for _ in changeInfos:
                changeInfoitem = EasyDict()
                changeInfoitem.changeTime = "".join(_.xpath('.//td[2]//text()')).replace("\n","").replace(" ","")
                changeInfoitem.changeItem = "".join(_.xpath('.//td[3]//text()')).replace("\n","").replace(" ","")
                changeInfoitem.changeBefore = "".join(_.xpath('.//td[4]//text()')).replace("\n","").replace(" ","")
                changeInfoitem.changeAfter = "".join(_.xpath('.//td[5]//text()')).replace("\n","").replace(" ","")
                changeInfo.append(changeInfoitem)
        else:
            pass


        #基本信息
        item.base = {
            "baseInfo": {
                "companyEmail": "".join(etre.xpath('//*[contains(text(),"邮箱")]/following-sibling::span[1]/text()')).replace('\n','').strip(' ').replace(" ","").replace("-",""),
                "creditCode": "".join(etre.xpath('//*[contains(text(),"信用代码")]/following-sibling::td[1]/text()')).replace('\n','').strip(' ').replace(" ",""),
                "OrganizationCode": "".join(etre.xpath('//*[contains(text(),"组织机构代码")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "registerNum": "".join(etre.xpath('//*[contains(text(),"注册号")]/following-sibling::td[1]/text()')).replace('\n','').strip(' ').replace(" ","").replace("-",""),
                "businessState": item.businessState,
                "industry": "".join(etre.xpath('//*[contains(text(),"所属行业")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "registerTime": "".join(etre.xpath('//*[contains(text(),"成立日期")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "companyType": "".join(etre.xpath('//*[contains(text(),"企业类型")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "businessTimeout": "".join(etre.xpath('//*[contains(text(),"营业期限")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "legalMan": "".join(etre.xpath('//h2[@class="seo font-20"]/text()')).replace('\n','').strip(' '),
                "confirmTime": "".join(etre.xpath('//*[contains(text(),"核准日期")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "registerMoney": "".join(etre.xpath('//*[contains(text(),"注册资本")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "registOrgan": "".join(etre.xpath('//section//*[contains(text(),"登记机关")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "registerAddress": "".join(etre.xpath('//section//*[contains(text(),"企业地址")]/following-sibling::td[1]/text()')).replace('\n','').strip(' '),
                "businessScope": "".join(etre.xpath('//section//*[contains(text(),"经营范围")]/following-sibling::td[1]/text()')).replace('\n','').strip(' ')
            },
            "holderInfoCount": holderInfo_count,
            "holderInfo": holderInfo,

            "employeeInfo": employeeInfo,
            "employeeInfoCount": employeeInfo_count,
            "changeInfo":changeInfo ,
            "changeInfoCount":changeInfo_count ,
            "branchInfo": branchInfo,
            "branchInfoCount": branchInfo_count,
        }

    def legal_text_info_parse(self,legal_text, item, legal_urls):
        """
        解析法律内容信息
        :return:
        """
        etre = HTML(legal_text.text)

        #裁判文书 1
        lawSuitsInfo = []
        lawsus = etre.xpath('//section[@id="wenshulist"]/table//tr[1]/following-sibling::tr')
        lawSuitsInfoCount = ""
        if lawsus:
            lawSuitsInfoCount = len(lawsus)
            for _ in lawsus:
                laws = EasyDict()
                laws.cpwNames = "".join(_.xpath("./td[2]//text()"))
                laws.cpwsResult = "".join(_.xpath("./td[3]//text()"))
                laws.cpwsMaster = "".join(_.xpath("./td[4]//text()"))
                laws.cpwsTime = "".join(_.xpath("./td[5]//text()"))
                laws.cpwNum = "".join(_.xpath("./td[6]//text()"))
                laws.cpwsJudge = "".join(_.xpath("./td[7]//text()"))
                laws.cpwsCourt = "".join(_.xpath("./td[8]//text()"))
                lawSuitsInfo.append(laws)


        #开庭公告 1
        courtNoticeInfo = []
        courts = etre.xpath('//section[@id="noticelist"]/table//tr[1]/following-sibling::tr')
        courtNoticeInfoCount = ""
        if courts:
            courtNoticeInfoCount = len(courts)
            for _ in courts:
                cour = EasyDict()
                cour.aCaseNum = "".join(_.xpath("./td[2]//text()"))
                cour.aLawfulDay = "".join(_.xpath("./td[3]//text()"))
                cour.aCaseReason = "".join(_.xpath("./td[4]//text()"))
                cour.aAppellor = "".join(_.xpath("./td[5]//text()")).replace("\n","").replace(" ","").replace("}","")
                cour.aDefendant = "".join(_.xpath("./td[6]//text()")).replace("\n","").replace(" ","").replace("}","")
                courtNoticeInfo.append(cour)

        #被执行人 1
        executedPersonInfo = []
        executedPersonInfos = etre.xpath('//section[@id="zhixinglist"]/table//tr[1]/following-sibling::tr')
        executedPersonInfoCount = ""
        if executedPersonInfos:
            executedPersonInfoCount = len(executedPersonInfos)
            for _ in executedPersonInfos:
                executed = EasyDict()
                executed.zCaseNum = "".join(_.xpath('./td[2]//text()'))
                executed.zCaseTime = "".join(_.xpath('./td[3]//text()'))
                executed.zCourt = "".join(_.xpath('./td[4]//text()'))
                executed.zTarget = "".join(_.xpath('./td[5]//text()'))
                executedPersonInfo.append(executed)

        # 法院公告 1
        noticesInfo = []

        notices = etre.xpath('//section[@id="gonggaolist"]/table//tr[1]/following-sibling::tr')
        noticesInfoCount = ""
        if notices:
            noticesInfoCount = len(notices)
            for _ in notices:
                notice = EasyDict()
                notice.appellor = "".join(_.xpath("./td[2]//text()")).replace("\n","").replace(" ","")
                notice.by_appellor = "".join(_.xpath("./td[3]//text()")).replace("\n","").replace(" ","")
                notice.cType = "".join(_.xpath("./td[4]//text()")).replace("\n","").replace(" ","")
                notice.cJudge = "".join(_.xpath("./td[5]//text()")).replace("\n","").replace(" ","")
                notice.cDate = "".join(_.xpath("./td[6]//text()")).replace("\n","").replace(" ","")
                noticesInfo.append(notice)

        #失信信息 1
        executionInfo = []
        executionInfos = etre.xpath('//section[@id="shixinlist"]/table//tr[1]/following-sibling::tr')
        executionInfoCount = "".join(etre.xpath('//section[@id="shixinlist"]/div/span[@class="tbadger"]/text()'))

        if executionInfos:

            for execu in executionInfos:
                execut = EasyDict()

                info_id = "".join(execu.xpath('./td[2]/a/@onclick'))
                if info_id != "":
                    info_id = info_id.split(",")[1].replace('"',"").replace(")","").strip(" ")
                    execu_url = "https://www.qichacha.com/company_shixinRelat?id=" + info_id
                    while 1:
                        response = self.f.get_req(url=execu_url,proxies=self.proxy)
                        if response:
                            exec_etr = HTML(response.text)
                            execut.by_appellor = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[1]/td[2]/text()'))
                            execut.diIdentify = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[1]/td[4]/text()'))

                            execut.diCourt = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[2]/td[2]/text()'))
                            execut.diPerform = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[2]/td[4]/text()'))

                            execut.dProvince = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[3]/td[2]/text()'))
                            execut.diDepend = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[3]/td[4]/text()'))


                            execut.diTime = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[4]/td[2]/text()'))
                            execut.diNum = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[4]/td[4]/text()'))

                            execut.Unit  = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[5]/td[2]/text()'))
                            execut.diPublishTime = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[5]/td[4]/text()'))


                            execut.diStatus = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[6]/td[2]/text()'))
                            execut.diDuty = "".join(exec_etr.xpath('//table[@class="ntable"]/tr[7]/td[2]/text()'))
                            break
                        else:
                            self.get_pro()
                    executionInfo.append(execut)

        # 股权冻结 1
        equityFreezeInfo = []

        equityFreezeInfos = etre.xpath('//section[@id="assistancelist"]/table//tr[1]/following-sibling::tr')
        equityFreezeInfoCount = ""
        if equityFreezeInfos:
            equityFreezeInfoCount = len(equityFreezeInfos)
            for _ in equityFreezeInfos:
                equity = EasyDict()
                equity.frzAppelor = "".join(_.xpath('./td[2]//text()'))
                equity.frzName = "".join(_.xpath('./td[3]//text()'))
                equity.frzPHNum = "".join(_.xpath('./td[4]//text()'))
                equity.frzNum = "".join(_.xpath('./td[5]//text()'))
                equity.frzCourt = "".join(_.xpath('./td[6]//text()'))
                equity.frzType = "".join(_.xpath('./td[7]//text()'))
                equityFreezeInfo.append(equity)

        # 立案信息
        caseInfo = []

        caseInfos = etre.xpath('//section[@id="lianlist"]/table//tr[1]/following-sibling::tr')
        caseInfoCount = ""
        if caseInfo:
            caseInfoCount =len(caseInfos)
            for _ in caseInfos:
                caseInfo_dict = EasyDict()
                caseInfo_dict.caseNum = "".join(_.xpath('./td[1]/text()'))
                caseInfo_dict.caseTime = "".join(_.xpath('./td[2]/text()'))
                caseInfo_dict.appellor = "".join(_.xpath('./td[3]/text()'))
                caseInfo_dict.by_appellor = "".join(_.xpath('./td[4]/text()'))
                caseInfo.append(caseInfo_dict)

        item.lawDangerous = {
            "lawSuitsInfoCount" : lawSuitsInfoCount,
            "lawSuitsInfo" : lawSuitsInfo,
            "courtNoticeInfoCount" : courtNoticeInfoCount,
            "courtNoticeInfo" : courtNoticeInfo,
            "executedPersonInfoCount" : executedPersonInfoCount,
            "executedPersonInfo" : executedPersonInfo,
            "noticesInfoCount" : noticesInfoCount,
            "noticesInfo" : noticesInfo,
            "executionInfoCount" : executionInfoCount,
            "executionInfo" : executionInfo,
            "equityFreezeInfoCount" : equityFreezeInfoCount,
            "equityFreezeInfo" : equityFreezeInfo,
            "caseInfoCount" : caseInfoCount,
            "caseInfo" : caseInfo,
        }

    def bus_sate_text_info_parse(self,bus_sate_text, item, bus_sate_urls):
        """
        解析经营状况数据信息
        :param bus_sate_text:
        :param item:
        :param bus_sate_urls:
        :return:
        """
        etre = HTML(bus_sate_text.text)

        #行政许可 [工商局]
        AdminPremGs = []
        AdminPremGs_lt = etre.xpath('//section[@id="licenslist"]/table/tr[1]/following-sibling::tr')

        AdminPremGsCount = ""
        if AdminPremGs_lt:
            AdminPremGsCount = len(AdminPremGs_lt)
            for _ in AdminPremGs_lt:
                Adm = EasyDict()
                judge = len(_)
                if judge > 0:
                    Adm.FileNum = "".join(_.xpath('./td[2]//text()'))
                    Adm.FileName = "".join(_.xpath('./td[3]//text()'))
                    Adm.StartIndate = "".join(_.xpath('./td[4]//text()'))
                    Adm.EndIndate = "".join(_.xpath('./td[5]//text()'))
                    Adm.PermOffice = "".join(_.xpath('./td[6]//text()'))
                    Adm.PermContent = "".join(_.xpath('./td[7]//text()'))
                    AdminPremGs.append(Adm)


        #行政许可 [信用中国]
        # AdminPremXyzg = []
        #
        # AdminPremXyzg_lt = etre.xpath('//section[@id="licenslist"]/following-sibling::section[1]/table/tr[1]/following-sibling::tr')
        # AdminPremXyzgCount = ""
        # if AdminPremXyzg_lt:
        #     AdminPremXyzgCount = len(AdminPremXyzg_lt)
        #     for _ in AdminPremXyzg_lt:
        #         Admi = EasyDict()
        #         judge = len(_)
        #         if judge > 0:
        #             info_id = "".join(_.xpath('./td/a/@onclick')).split("(")[1].replace(")","").replace('"',"").replace(" ","")
        #             while 1:
        #                 data = {
        #                     "id" : info_id,
        #                 }
        #                 response = self.f.post_req(url="https://www.qichacha.com/company_xzxukeView",data=data,proxies=self.proxy)
        #                 if response:
        #                     result = json.loads(response.text)["data"]
        #                     Admi.company_name = result["company_name"]
        #                     Admi.document_no = result["document_no"]
        #                     Admi.name = result["name"]
        #                     Admi.type = result["type"]
        #                     Admi.content = result["content"]
        #                     Admi.office_no = result["office_no"]
        #                     Admi.decide_date = result["decide_date"]
        #                     Admi.expire_date = result["expire_date"]
        #                     Admi.status = result["status"]
        #                     Admi.province = result["province"]
        #
        #                     AdminPremXyzg.append(Admi)
        #                 else:
        #                     self.get_pro()

        #税务信用
        RevenueCredit = []
        RevenueCredit_lt = etre.xpath('//section[@id="taxCreditList"]/table/tr[1]/following-sibling::tr')
        RevenueCreditCount = ""
        if RevenueCredit_lt:
            RevenueCreditCount = len(RevenueCredit_lt)
            for _ in RevenueCredit_lt:
                Revenue = EasyDict()
                judge = len(_)
                if judge > 0:
                    Revenue.EstimateYear = "".join(_.xpath('./td[2]//text()'))
                    Revenue.TaxesNim = "".join(_.xpath('./td[3]//text()'))
                    Revenue.TaxesLevel = "".join(_.xpath('./td[4]//text()'))
                    Revenue.EstimateUnits = "".join(_.xpath('./td[5]//text()'))
                    RevenueCredit.append(Revenue)

        #招投标信息
        TenderMessage = []
        TenderMessage_lt = etre.xpath('//section[@id="tenderlist"]/table/tbody/tr/following-sibling::tr')
        TenderMessageCount = ""
        if TenderMessage_lt:
            TenderMessageCount = len(TenderMessage_lt)
            for _ in TenderMessage_lt:
                Tender = EasyDict()
                judge = len(_)
                if judge > 0:
                    Tender.Describe = "".join(_.xpath('./td[2]//text()'))
                    Tender.Release = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').strip(' ')
                    Tender.Regin = "".join(_.xpath('./td[4]//text()'))
                    Tender.PrijectCate = "".join(_.xpath('./td[5]//text()'))
                    TenderMessage.append(Tender)

        #财务总览
        Finance = []

        Finance_lt = etre.xpath('//section[@id="V3_cwzl"]/table/tr')
        FinanceCount = ""
        if Finance_lt:
            FinanceCount = len(Finance_lt)
            Fina = EasyDict()
            Fina.Strength = etre.xpath('//section[@id="V3_cwzl"]/table/tr[1]/td[2]/text()')
            Fina.TaxesRange = etre.xpath('//section[@id="V3_cwzl"]/table/tr[1]/td[4]/text()')
            Fina.ProfitMargin = etre.xpath('//section[@id="V3_cwzl"]/table/tr[2]/td[2]/text()')
            Fina.Gross = etre.xpath('//section[@id="V3_cwzl"]/table/tr[2]/td[4]/text()')
            Finance.append(Fina)

        #新闻舆情
        News = []
        News_lt = etre.xpath('//section[@id="newslist"]/table/tr')
        NewsCount = ""
        if News_lt:
            NewsCount = len(News_lt)
            for _ in News_lt:
                new = EasyDict()
                new.NewTitle = "".join(_.xpath('./td/a/div/div[1]/span[2]/text()'))
                new.NewTags = "".join(_.xpath('./td/a/div/div[2]//text()'))
                new.NewSite = "".join(_.xpath('./td/a/div/small/text()')).replace('\n','').replace('\r','').strip(' ')
                new.NewUri = "".join(_.xpath('./td//a/@href'))
                new.NewReleseTime = "".join(_.xpath('./td/a/div/small/span/text()'))
                News.append(new)


        #公告研报
        Notice = []

        Notice_lt = etre.xpath('//section[@id="yblist"]/table/tbody/tr[1]/following-sibling::tr')
        NoticeCount = ""
        if Notice_lt:
            NoticeCount = len(Notice_lt)
            for _ in Notice_lt:
                Noti = EasyDict()
                Noti.Ncontent = "".join(_.xpath('./td[2]//text()')).replace('\n','').replace('\r','').strip(' ')
                Noti.Ncate = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').strip(' ')
                Noti.Ndate = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\r','').strip(' ')
                Notice.append(Noti)

        #债券信息
        Debt = []
        Debt_lt = etre.xpath('//section[@id="creditorlist"]/table/tbody/tr[1]/following-sibling::tr')
        DebtCount = ""
        if Debt_lt:
            DebtCount = len(Debt_lt)
            for _ in Debt_lt:
                Deb = EasyDict()
                Deb.bond = "".join(_.xpath('.//td[2]//text()')).replace('\n','').replace('\r','').strip(' ')
                Deb.bondCode = "".join(_.xpath('.//td[3]//text()')).replace('\n','').replace('\r','').strip(' ')
                Deb.bondType = "".join(_.xpath('.//td[4]//text()')).replace('\n','').replace('\r','').strip(' ')
                Deb.issue = "".join(_.xpath('.//td[5]//text()')).replace('\n','').replace('\r','').strip(' ')
                Deb.appear = "".join(_.xpath('.//td[6]//text()')).replace('\n','').replace('\r','').strip(' ')
                Debt.append(Deb)

        item.development ={
            "AdminPremGs":AdminPremGs,
            "AdminPremGsCount":AdminPremGsCount,
            "RevenueCredit":RevenueCredit,
            "RevenueCreditCount":RevenueCreditCount,
            "TenderMessage":TenderMessage,
            "TenderMessageCount":TenderMessageCount,
            "Finance":Finance,
            "FinanceCount":FinanceCount,
            "News":News,
            "NewsCount":NewsCount,
            "Notice":Notice,
            "NoticeCount":NoticeCount,
            "Debt":Debt,
            "DebtCount":DebtCount,
        }

    def bus_risks_text_info_parse(self,bus_risks_text, item, bus_sate_urls):
        """
        解析经营风险数据信息
        :param bus_sate_text:
        :param item:
        :param bus_sate_urls:
        :return:
        """
        etre = HTML(bus_risks_text.text)

        #股权出质
        Stock = []

        Stock_lt = etre.xpath('//section[@id="pledgelist"]/table/tr[1]/following-sibling::tr')
        StockCount = ""
        if Stock_lt:
            StockCount = len(Stock_lt)
            for _ in Stock_lt:
                Stoc = EasyDict()
                Stoc.RegNumber = "".join(_.xpath('./td[2]//text()'))
                Stoc.Pledgor = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\t','').strip(' ')
                Stoc.Pawnee = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\t','').strip(' ')
                Stoc.PledCompany = "".join(_.xpath('./td[5]//text()')).replace('\n','').replace('\t','').strip(' ')
                Stoc.PledRMB = "".join(_.xpath('./td[6]//text()'))
                Stoc.RegDate = "".join(_.xpath('./td[7]//text()'))
                Stoc.State = "".join(_.xpath('./td[8]//text()'))
                Stock.append(Stoc)

        #行政处罚 [工商局]
        GpPnalty = []

        GpPnalty_lt = etre.xpath('//section[@id="penaltylist"]/table/tr[1]/following-sibling::tr')
        GpPnaltyCount = ""
        if GpPnalty_lt:
            GpPnaltyCount = len(GpPnalty_lt)
            for _ in GpPnalty_lt:
                GpP = EasyDict()
                GpP.Number = "".join(_.xpath('./td[2]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                GpP.Type = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                GpP.Content = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                GpP.Pubdate = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                GpP.Decoffic = "".join(_.xpath('./td[6]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                GpP.Decdate = "".join(_.xpath('./td[7]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                GpPnalty.append(GpP)

        #行政处罚 [信用中国]
        XyzgPnalty = []

        XyzgPnalty_lt = etre.xpath('//section[@id="penaltylist"]/following-sibling::*[1]/table/tr[1]/following-sibling::tr')
        XyzgPnaltyCount = ""
        if XyzgPnalty_lt:
            XyzgPnaltyCount = len(XyzgPnalty_lt)
            for _ in XyzgPnalty_lt:
                XyzgPna = EasyDict()
                XyzgPna.Number = "".join(_.xpath('./td[2]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                XyzgPna.Name = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                XyzgPna.Addr = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                XyzgPna.Date = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\t', '').strip(' ')
                XyzgPnalty.append(XyzgPna)

        item.developmentrisk = {
            "Stock":Stock,
            "StockCount":StockCount,
            "GpPnalty":GpPnalty,
            "GpPnaltyCount":GpPnaltyCount,
            "XyzgPnalty": XyzgPnalty,
            "XyzgPnaltyCount": XyzgPnaltyCount,
        }

    def corporate_text_info_parse(self,corporate_text, item, corporate_url):
        """
        解析企业发展数据信息
        :param corporate_text:
        :param item:
        :param corporate_url:
        :return:
        """
        etre = HTML(corporate_text.text)


        #企业基本信息
        EnterpriseBase = []

        EnterpriseBase_lt = etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr')
        EnterpriseBaseCount = ""
        if EnterpriseBase_lt:
            EnterpriseBaseCount = len(EnterpriseBase_lt)
            Enterp = EasyDict()
            Enterp.RegNumber = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[1]/td[2]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.CreditCode = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[1]/td[4]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.MangSate = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[2]/td[2]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.MangPhone = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[2]/td[4]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.NumPeo = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[3]/td[2]/text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.Postal = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[3]/td[4]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.StockTransfer = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[4]/td[2]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.StockPurchase = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[4]/td[4]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.Email = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[5]/td[2]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            Enterp.CompanyAddr = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业基本信息")]/parent::div/following-sibling::table[1]/tbody/tr[6]/td[2]//text()')).replace('\r','').replace('\n','').replace('\t','').strip(' ')
            EnterpriseBase.append(Enterp)

        #网站或网店信息
        Site = []

        Site_lt = etre.xpath('//div[@id="0"]//h3[contains(text(),"网站或网店信息")]/parent::div/following-sibling::table[1]/tr[1]/following-sibling::tr')
        SiteCount = ""
        if Site_lt:
            SiteCount = len(Site_lt)
            for _ in Site_lt:
                Sit = EasyDict()
                Sit.Type = "".join(_.xpath('./td[2]//text()')).replace('\r', '').replace('\n', '').replace('\t', '').strip(' ')
                Sit.Name = "".join(_.xpath('./td[3]//text()')).replace('\r', '').replace('\n', '').replace('\t', '').strip(' ')
                Sit.NetworkAddr = "".join(_.xpath('./td[4]//text()')).replace('\r', '').replace('\n', '').replace('\t', '').strip(' ')
                Site.append(Sit)

        #股东（发起人）出资信息
        StockholderRatio = []

        StockholderRatio_lt = etre.xpath('//div[@id="0"]//h3[contains(text(),"股东（发起人）出资信息")]/parent::div/following-sibling::table[1]/tbody/tr[1]/following-sibling::tr')
        StockholderRatioCount = ""
        if StockholderRatio_lt:
            StockholderRatioCount = len(StockholderRatio_lt)
            for _ in StockholderRatio_lt:
                Stockholder = EasyDict()
                Stockholder.Initiator = "".join(_.xpath('./td[2]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                Stockholder.SubLimit = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                Stockholder.SubDate = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                Stockholder.SubMethod = "".join(_.xpath('./td[5]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                Stockholder.PaidLimit = "".join(_.xpath('./td[6]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                Stockholder.PaidDate = "".join(_.xpath('./td[7]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                Stockholder.PaidMethod = "".join(_.xpath('./td[8]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                StockholderRatio.append(Stockholder)

        #对外投资信息
        Outbrand = []
        Outbrand_lt = etre.xpath('//div[@id="0"]//h3[contains(text(),"对外投资信息")]/parent::div/following-sibling::table[1]/tbody/tr[1]/following-sibling::tr')
        OutbrandCount = ""
        if Outbrand_lt:
            OutbrandCount = len(Outbrand_lt)
            for _ in Outbrand_lt:
                Outb = EasyDict()
                Outb.CName = "".join(_.xpath('./td[2]//text()')).replace('\n','').replace('\r','').strip(' ')
                Outb.Cnumber = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').strip(' ')
                Outbrand.append(Outb)


        #企业资产状况信息
        EnterpriseStateInfo = []
        Enterprise = EasyDict()
        Enterprise.total = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[1]/td[2]//text()'))
        Enterprise.equity = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[1]/td[4]//text()'))
        Enterprise.gross = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[2]/td[2]//text()'))
        Enterprise.income = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[2]/td[4]//text()'))
        Enterprise.bunincome = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[3]/td[2]//text()'))
        Enterprise.retained = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[3]/td[4]//text()'))
        Enterprise.totaltax = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[4]/td[2]//text()'))
        Enterprise.totalliab = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"企业资产状况信息")]/parent::div/following-sibling::table[1]/tr[4]/td[4]//text()'))


        EnterpriseStateInfo.append(Enterprise)

        #股权变更信息
        StockChang = []

        StockChang_lt = etre.xpath('//div[@id="0"]//h3[contains(text(),"股权变更信息")]/parent::div/following-sibling::table[1]/tbody/tr[1]/following-sibling::tr')
        StockChangCount = ""
        if StockChang_lt:
            StockChangCount = len(StockChang_lt)
            for _ in StockChang_lt:
                StChang = EasyDict()
                StChang.Holder = "".join(_.xpath('./td[2]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                StChang.affter = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                StChang.end = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                StChang.date = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                StockChang.append(StChang)

        #修改记录
        ChangeBook = []

        ChangeBook_lt = etre.xpath('//div[@id="0"]//h3[contains(text(),"修改记录")]/parent::div/following-sibling::table[1]/tbody/tr[1]/following-sibling::tr')
        ChangeBookCount = ""
        if ChangeBook_lt:
            ChangeBookCount = len(ChangeBook_lt)
            for _ in ChangeBook_lt:
                Chbook = EasyDict()
                Chbook.event = "".join(_.xpath('./td[2]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                Chbook.affter = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                Chbook.end = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                Chbook.date = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                ChangeBook.append(Chbook)

        #社保信息
        Socail = []
        Socail_dict = EasyDict()

        Socail_dict.cityInsurance = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"社保信息")]/parent::div/following-sibling::table[1]/tbody/tr[1]/td[2]//text()'))
        Socail_dict.medInsurance = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"社保信息")]/parent::div/following-sibling::table[1]/tbody/tr[1]/td[4]//text()'))
        Socail_dict.birthInsurance = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"社保信息")]/parent::div/following-sibling::table[1]/tbody/tr[2]/td[2]//text()'))
        Socail_dict.unempInsurance = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"社保信息")]/parent::div/following-sibling::table[1]/tbody/tr[2]/td[4]//text()'))
        Socail_dict.occupInsurance = "".join(etre.xpath('//div[@id="0"]//h3[contains(text(),"社保信息")]/parent::div/following-sibling::table[1]/tbody/tr[3]/td[2]//text()'))
        Socail.append(Socail_dict)

        #融资信息
        Fininfo = []

        Fininfo_lt = etre.xpath('//section[@id="financingInfo"]//table/th[last()]/following-sibling::tr')
        FininfoCount = ""
        if Fininfo_lt:
            FininfoCount = len(Fininfo_lt)
            for _ in Fininfo_lt:
                Finin = EasyDict()
                Finin.date = "".join(_.xpath('./td[2]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Finin.name = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Finin.num = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Finin.money = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Finin.investor = "".join(_.xpath('./td[6]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Finin.new = "".join(_.xpath('./td[7]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Fininfo.append(Finin)

        #投资机构
        Inves = []

        Inves_lt = etre.xpath('//section[@id="investAgencyInfo"]//table/tr[1]/following-sibling::tr')
        InvesCount = ""
        if Inves_lt:
            InvesCount = len(Inves_lt)
            for _ in Inves_lt:
                Inve = EasyDict()
                Inve.name = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Inve.date = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Inve.addr = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Inve.info = "".join(_.xpath('./td[6]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                Inves.append(Inve)

        #核心人员

        CorePer = []

        CorePer_lt = etre.xpath('//section[@id="memberInfo"]//table/tr[1]/following-sibling::tr')
        CorePerCount = ""
        if CorePer_lt:
            CorePerCount = len(CorePer_lt)
            for _ in CorePer_lt:
                CrPer = EasyDict()
                CrPer.name = "".join(_.xpath('./td[2]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                CrPer.level = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                CrPer.info = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\r', '').strip(' ')
                CorePer.append(CrPer)

        #企业业务
        companyBus = []

        companyBus_lt = etre.xpath('//section[@id="productInfo"]//table/tr[1]/following-sibling::tr')
        companyBusCount = ""
        if companyBus_lt:
            companyBusCount = len(companyBus_lt)
            for _ in companyBus_lt:
                compyBus = EasyDict()
                compyBus.name = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compyBus.fininfo = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compyBus.date = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compyBus.addr = "".join(_.xpath('./td[6]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compyBus.info = "".join(_.xpath('./td[7]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                companyBus.append(compyBus)

        #竞品信息
        compeinfo = []

        compeinfo_lt = etre.xpath('//section[@id="compatProductInfo"]//table/tr[1]/following-sibling::tr')
        compeinfoCount = ""
        if compeinfo_lt:
            compeinfoCount = len(compeinfo_lt)
            for _ in compeinfo_lt:
                compe = EasyDict()
                compe.name = "".join(_.xpath('./td[3]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compe.fininfo = "".join(_.xpath('./td[4]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compe.date = "".join(_.xpath('./td[5]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compe.addr = "".join(_.xpath('./td[6]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compe.info = "".join(_.xpath('./td[7]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compe.affi = "".join(_.xpath('./td[8]//text()')).replace('\n', '').replace('\r', '').replace('\t','').replace(' ','')
                compeinfo.append(compe)

        item.corporate ={
            "EnterpriseBase":EnterpriseBase,
            "EnterpriseBaseCount":EnterpriseBaseCount,

            "Site_lt" :Site_lt,
            "SiteCount" :SiteCount,

            "StockholderRatio":StockholderRatio,
            "StockholderRatioCount":StockholderRatioCount,

            "Outbrand":Outbrand,
            "OutbrandCount":OutbrandCount,

            "EnterpriseStateInfo":EnterpriseStateInfo,
            "StockChang" :StockChang,
            "StockChangCount" :StockChangCount,
            "ChangeBook" :ChangeBook,
            "ChangeBookCount" :ChangeBookCount,
            "Socail":Socail,
            "Fininfo":Fininfo,
            "FininfoCount":FininfoCount,
            "Inves" :Inves,
            "Inves_lt":Inves_lt,
            "InvesCount":InvesCount,
            "CorePer":CorePer,
            "CorePerCount":CorePerCount,
            "companyBus":companyBus,
            "companyBusCount":companyBusCount,
            "compeinfo":compeinfo,
            "compeinfoCount":compeinfoCount,

        }

    def intellectual_text_info_parse(self,intellectual_text, item, intellectual_urls):
        """
        解析知识产权数据信息
        :return:
        """
        etre = HTML(intellectual_text.text)

        #商标信息
        brandInfo = []

        brandInfo_lt = etre.xpath('//section[@id="shangbiaolist"]//table//tr[1]/following-sibling::tr')
        brandInfoCount = ""
        if brandInfo_lt:
            brandInfoCount = len(brandInfo_lt)
            for _ in brandInfo_lt:
                bran = EasyDict()
                bran.name = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                bran.sate = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                bran.date = "".join(_.xpath('./td[5]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                bran.num = "".join(_.xpath('./td[6]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                bran.cate = "".join(_.xpath('./td[7]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                bran.info = "".join(_.xpath('./td[8]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                brandInfo.append(bran)

        #证书信息
        certiInfo = []
        certiInfo_lt = etre.xpath('//section[@id="zhengshulist"]//table/tr[1]/following-sibling::tr')
        certiInfoCount = ""
        if certiInfo_lt:
            certiInfoCount = len(certiInfo_lt)
            for _ in certiInfo_lt:
                certi = EasyDict()
                certi.type = "".join(_.xpath('./td[2]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                certi.name = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                certi.num = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                certi.startdate = "".join(_.xpath('./td[5]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                certi.enddate = "".join(_.xpath('./td[6]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')

                certiInfo.append(certi)

        #作品著作权
        productionInfo = []

        productionInfo_lt = etre.xpath('//section[@id="zzqlist"]//table/tr[1]/following-sibling::tr')
        productionInfoCount = ""
        if productionInfo_lt:
            productionInfoCount = len(productionInfo_lt)
            for _ in productionInfo_lt:
                prod = EasyDict()
                prod.name = "".join(_.xpath('./td[2]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                prod.startRelaseDate = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                prod.endRelaseDate = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                prod.num = "".join(_.xpath('./td[5]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                prod.date = "".join(_.xpath('./td[6]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                prod.cate = "".join(_.xpath('./td[7]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')

                productionInfo.append(prod)

        #软件著作权
        sotware = []

        sotware_lt = etre.xpath('//section[@id="rjzzqlist"]//table/tr[1]/following-sibling::tr')
        sotwareCount = ""
        if sotware_lt:
            sotwareCount = len(sotware_lt)
            for _ in sotware_lt:
                sot = EasyDict()
                sot.name = "".join(_.xpath('./td[2]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                sot.version = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                sot.relasename = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                sot.named = "".join(_.xpath('./td[5]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                sot.num = "".join(_.xpath('./td[6]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                sot.date= "".join(_.xpath('./td[7]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')

                sotware.append(sot)

        #网站信息
        siteInfo = []

        siteInfo_lt = etre.xpath('//section[@id="websitelist"]//table/tr[1]/following-sibling::tr')
        siteInfoCount = ""
        if siteInfo_lt:
            siteInfoCount = len(siteInfo_lt)
            for _ in siteInfo_lt:
                site = EasyDict()
                site.name = "".join(_.xpath('./td[2]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                site.networke = "".join(_.xpath('./td[3]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                site.domain = "".join(_.xpath('./td[4]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                site.license = "".join(_.xpath('./td[5]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')
                site.date = "".join(_.xpath('./td[6]//text()')).replace('\n','').replace('\r','').replace('\t','').strip(' ')


                siteInfo.append(site)

        item.intellectual = {
            "brandInfo":brandInfo,
            "brandInfoCount":brandInfoCount,
            "certiInfo":certiInfo,
            "certiInfoCount":certiInfoCount,
            "productionInfo":productionInfo,
            "productionInfoCount":productionInfoCount,
            "sotware":sotware,
            "sotwareCount":sotwareCount,
            "siteInfo":siteInfo,
            "siteInfoCount":siteInfoCount
        }

    def code(self,action):
        """
        验证滑块
        :return:
        """
        swipe_button = self.borser.find_element_by_id("nc_1_n1z")
        action.click_and_hold(swipe_button)  # perform用来执行ActionChains中存储的行为
        action.move_by_offset(400, 0).perform()  # 移动滑块
        time.sleep(2)

    def czpf(self,action):
        """
        出现次数过多
        :param action:
        :return:
        """
        while 1:
            try:
                self.code(action)
                self.borser.find_element_by_id("verify").click()
                break
            except:
                pass

    def smdl(self,action):
        """
        出现滑块
        :param action:
        :return:
        """

        self.borser.find_element_by_id("normalLogin").click()
        while 1:
            try:
                self.borser.find_element_by_id("nameNormal").send_keys("17076937059")
                self.borser.find_element_by_id("pwdNormal").send_keys("dgg123456")

                self.code(action)
                self.borser.find_elements_by_css_selector(".login-btn")[0].click()
                break
            except:
                self.borser.refresh()

    def run(self):
        self.get_pro()
        count = KEYS_DB.find({"flag": 0}).count()
        while count:

            try:
                # company_key = "深圳市宏力捷电子有限公司"
                # company_key = "湖北三峡农村商业银行股份有限公司"
                # company_key = "阿里巴巴"
                # url = "https://www.qichacha.com/gongsi_mindlist?type=mind&searchKey={}&searchType=0".format(company_key)
                # self.f.session.headers.update({
                #     "Referer":"https://www.qichacha.com/",
                # })
                # resp = self.f.get_req(url=url,proxies=self.proxy)
                # if resp != False:
                #     time.sleep(1)
                #     respcookie = resp.headers["Set-Cookie"]
                #     updated = int(time.time()*1000)
                #     sid = int(time.time()*1000)
                #     info = int(time.time()*1000)
                #     datas = {
                #         "sid": sid,
                #         "updated": updated,
                #         "info": info,
                #         "superProperty": "{}",
                #         "platform": "{}",
                #         "utm": "{}",
                #         "referrerDomain": "www.qichacha.com"
                #     }
                #     cookie =respcookie + "zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=" + str(datas)
                #     self.f.session.headers.update({
                #         "Cookie": cookie,
                #         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                #         "Connection": "keep-alive",
                #         "Upgrade-Insecure-Requests": "1",
                #     })
                #
                #     info_parmas, company_infos = self.search_parmas(company_key)
                #     if info_parmas != [] and company_infos != []:
                # 初始化driver
                self.borser = self.chrome_driver()
                # 最小化窗口
                self.borser.minimize_window()
                # 清除缓存
                # self.borser.delete_all_cookies()

                mogodata = KEYS_DB.find_one({"flag": 0})
                # company_key = "佳木斯益隆煤矿机械制造有限公司"
                company_key = mogodata["所属公司"]

                self.borser.get(url="https://www.qichacha.com/user_login")
                action = ActionChains(self.borser)
                self.smdl(action)

                time.sleep(4)


                self.borser.find_element_by_css_selector('.close').click()
                time.sleep(2)

                self.borser.find_element_by_xpath("//*[@id='index']/preceding-sibling::input").send_keys(company_key)
                self.borser.find_element_by_id("V3_Search_bt").click()



                if "您的操作过于频繁，验证后再操作" in self.borser.page_source:
                    self.czpf(action)

                # elif "法人或股东" not in self.borser.page_source:
                #
                #     self.smdl(action)


                element = WebDriverWait(self.borser, 5, 0.5).until(
                    EC.presence_of_element_located((By.ID, "searchlist")))

                cookie = self.borser.get_cookies()
                cookies = ""
                for items in cookie:
                    jioncook = items["name"] + "=" + items["value"] + "; "
                    cookies += jioncook
                print(cookies)

                #解析页面获取参数
                HTMLTEXT = self.borser.page_source
                # HTMLTEXT = resp.text
                etre = HTML(HTMLTEXT)

                info_parmas = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::*[1]/a/@onclick')  # pc端
                company_infos = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::*[1]/a/@href')

                self.f.session.headers.update({
                    "Cookie": cookies,
                })

                item = EasyDict()
                for _ in range(len(info_parmas)):
                    fol_result = (info_parmas[_].split("addSearchIndex")[1]).replace('(', '').replace(')', '').replace(
                        "'", '').replace(";", '')

                    fol_results = fol_result.split(',')
                    if mogodata["所属公司"] == fol_result.split(',')[0]:
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

                        # #法律信息
                        legal_urls = company_info_urls.replace("firm","csusong")
                        legal_text = self.company_info_req(legal_urls)
                        self.legal_text_info_parse(legal_text, item, legal_urls)

                        # #经营状况
                        bus_sate_urls = company_info_urls.replace("firm","crun")
                        bus_sate_text = self.company_info_req(bus_sate_urls)
                        self.bus_sate_text_info_parse(bus_sate_text, item, bus_sate_urls)

                        # #经营风险
                        bus_risks_url = company_info_urls.replace("firm","cfengxian")
                        bus_risks_text = self.company_info_req(bus_risks_url)
                        self.bus_risks_text_info_parse(bus_risks_text, item, bus_risks_url)

                        # #企业发展
                        corporate_url = company_info_urls.replace("firm","creport")
                        corporate_text = self.company_info_req(corporate_url)
                        self.corporate_text_info_parse(corporate_text, item, corporate_url)

                        #知识产权
                        intellectual_urls = company_info_urls.replace("firm","cassets")
                        intellectual_text = self.company_info_req(intellectual_urls)
                        self.intellectual_text_info_parse(intellectual_text, item, intellectual_urls)
                        print(item)

                        count -= 1
                self.borser.close()
            except:
                self.borser.close()













