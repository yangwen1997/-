from lxml.etree import HTML
from pymongo import MongoClient, DESCENDING
import asyncio
# from pyppeteer_dev.pyppeteer import launch
from pyppeteer import launch
import time

# count = 100

# ip_cli = MongoClient("mongodb://root:root962540@10.0.0.55:27017")
# ip_results_coll = ip_cli['ip_db']['ip_results']
# #阿布云代理
# def ABY_IP_():
#     """#
#     阿布云代理接入
#     :return:
#     """
#     proxyHost = "http-dyn.abuyun.com"
#     proxyPort = "9020"
#
#     # 代理隧道验证信息
#     proxyUser = "HQ74H343NC8P83MD"
#     proxyPass = "72425EBF9493543B"
#
#     proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
#         "host": proxyHost,
#         "port": proxyPort,
#         "user": proxyUser,
#         "pass": proxyPass,
#     }
#
#     proxies = {
#         "http": proxyMeta,
#         "https": proxyMeta,
#     }
#     return proxies
#




async def main():
    browser = await launch(headless=False)
    page = await browser.newPage()

    # await page.goto('https://www.qichacha.com')
    # await page.goto('http://wsjs.saic.gov.cn/txnT01.do?dRmFctOl=qmFWYhYhjSHB.R2Z9vSE9DJTTeYhEGyiXHVIjj7FJd8iPGsLdb5vUVE7_1_s.TrCPGrXPc5UBGWWZ5ltvq.gEvd4qnLwVe395S9PAeIbRjR3kNHwpTK4JBjLXPQknFApOTasYnKKib44aBnpNhLmQrsbqk6')
    await page.goto('https://www.tianyancha.com/')

    # await page.evaluate("document.getElementById('searchkey').value = '阿里巴巴'")
    time.sleep(1)
    # await page.evaluate("document.getElementById('V3_Search_bt').click()")
    # await page.evaluate("document.querySelector('#txnS03 > a').click()")
    await page.evaluate("document.querySelectorAll('.link-white')[2].click()")
    time.sleep(1)
    await page.evaluate("document.querySelectorAll('.title-tab>div')[1].click()")
    time.sleep(1)
    await page.evaluate("document.querySelectorAll('.position-rel>input')[2].value='%s'"%("123456789"))
    time.sleep(1)
    await page.evaluate("document.querySelectorAll('.-block>input')[0].value='%s'"%("123456789"))
    time.sleep(1)
    await page.evaluate("document.querySelectorAll('.in>div')[6].click()")


    # await page.goto('https://www.qichacha.com/search?key=阿里巴巴')
    # await page.screenshot({'path': 'example.png'})

    # print(cov)
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())
