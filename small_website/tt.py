from selenium import webdriver
from common import get_proxy, get_log
from random import choice
import time

log = get_log()

chrome_options = webdriver.ChromeOptions()
class QCC:
    def __init__(self):
        self.count = 1
        self.log = log
        self.borser = self.chrome_driver()


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
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('-no-sandbox')
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument('--disable-plugins-discovery')
        chrome_options.add_argument("--proxy-server=http://{}".format(ip))

        # 如果proxy_tag==1使用下面的配置方式，否则使用else下的配置方式

        # 实例化driver
        self.driver = webdriver.Chrome(
            chrome_options=chrome_options,
            executable_path = "D:\software\chrome\chromedriver\chromedriver.exe")
        # 设置页面等待超时时间（由于代理网络有时延时较高，所以设置等待超时时间为40s）
        self.driver.set_page_load_timeout(40)
        return  self.driver

    def run(self):

        self.borser.get(url="https://www.qichacha.com/")
        time.sleep(3)
        self.borser.find_element_by_xpath("//*[@id='index']/preceding-sibling::input").send_keys("阿里巴巴")
        self.borser.find_element_by_xpath("//*[@id='index']").click()
        time.sleep(5)
        self.borser.close()

START = QCC()
START.run()