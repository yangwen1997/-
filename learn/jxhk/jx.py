from selenium import webdriver
from common import get_proxy, get_log
from random import choice
from lxml.etree import HTML
from jxhk.feach import FEACH
from selenium.webdriver import ActionChains, FirefoxProfile
import time
import pymongo

log = get_log()

DATABASE = pymongo.MongoClient("mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017")
DB = DATABASE["qixin_com"]["m6-new_results"]
log = get_log()

# chrome_options = webdriver.FirefoxOptions()
# chrome_options = webdriver.ChromeOptions()
class QCC:
    def __init__(self):
        self.count = 1
        self.log = log
        self.f = FEACH()

        self.proxy = None


    def get_pro(self):
        """
        获取代理
        :return:
        """
        proxy = choice(get_proxy(1))["ip"]
        # self.proxy = {
        #     "http": "http://" + proxy,"https": "https://" + proxy,
        # }
        return proxy

    def chrome_driver(self):
        """
        实例化driver
        :return:
        """
        # 启动延时时间
        sleep_time = self.count*5
        self.log.info('延时{}s启动...'.format(sleep_time))
        # driver配置
        ip = self.get_pro()

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

    def get_pros(self):
        """
        获取代理
        :return:
        """
        proxy = choice(get_proxy(1))["ip"]
        self.proxy = {
            "http": "http://" + proxy,"https": "https://" + proxy,
        }
        # return proxy

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

        log.info("数据{}更新成功修改mongodb数据成功".format(item["_id"]))

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

    def code(self,action):
        """
        验证滑块
        :return:
        """
        swipe_button = self.borser.find_element_by_id("nc_1_n1z")
        action.click_and_hold(swipe_button)  # perform用来执行ActionChains中存储的行为
        action.move_by_offset(400, 0).perform()  # 移动滑块
        time.sleep(1)

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

        count = DB.find({"qcc_supplement": 0}).count()
        cookie_count = 0
        while count:



            #初始化driver
            self.borser = self.chrome_driver()
            #最小化窗口
            self.borser.minimize_window()
            #清除缓存
            # self.borser.delete_all_cookies()

            mogodata = DB.find_one({"qcc_supplement": 0})
            # company_key = "佳木斯益隆煤矿机械制造有限公司"
            company_key = mogodata["companyName"]

            self.borser.get(url="https://www.qichacha.com/")
            self.borser.find_element_by_xpath("//*[@id='index']/preceding-sibling::input").send_keys(company_key)
            self.borser.find_element_by_id("V3_Search_bt").click()
            action = ActionChains(self.borser)

            if "您的操作过于频繁，验证后再操作" in self.borser.page_source:
                self.czpf(action)

            elif "法人或股东" not in self.borser.page_source:

                self.smdl(action)


            cookie = self.borser.get_cookies()
            print(cookie)
            cookies = ""
            for items in cookie:
                jioncook = items["name"] + "=" + items["value"] + "; "
                cookies += jioncook
            print(cookies)

            time.sleep(2)
            HTMLTEXT = self.borser.page_source
            etre = HTML(HTMLTEXT)

            info_parmas = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::*[1]/a/@onclick')  # pc端
            company_infos = etre.xpath('//*[contains(@id,"search-result")]//td[contains(@class,"imgtd")]/following-sibling::*[1]/a/@href')

            self.f.session.headers.update({
                "Cookie": cookies,
            })

            self.proxy = self.get_pros()

            item = mogodata
            for _ in range(len(info_parmas)):

                fol_result = (info_parmas[_].split("addSearchIndex")[1]).replace('(', '').replace(')', '').replace("'",
                                                                                                                   '').replace(
                    ";", '')

                if mogodata["companyName"] == fol_result.split(',')[0]:

                    fol_results = fol_result.split(',')
                    company_info_url = company_infos[_]

                    data = {
                        "search_key": fol_results[0],
                        "search_index": fol_results[1],
                        "search_url": '',
                        "company_name": fol_results[2],
                        "type": fol_results[-1],
                    }

                    # 基本信息
                    company_info_urls = self.server_auth(data, company_info_url)
                    html_text = self.company_info_req(company_info_urls)
                    self.company_info_parse(html_text, item, company_info_urls)


            self.borser.close()
            count -= 1


START = QCC()
START.run()