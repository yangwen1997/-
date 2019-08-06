import requests
from fake_useragent import UserAgent
from lxml.etree import HTML
import hashlib
import time
import json
ua = UserAgent()


# urls = 'https://pages.tmall.com/wow/a/act/tmall/tmc/22351/wupr?spm=875.7931836/B.category201661812.1.659c42650pGCtU&wh_pid=industry-163144&acm=lb-zebra-148799-983674.1003.4.6142250&scm=1003.4.lb-zebra-148799-983674.OTHER_2_6142250'
s = requests.session()

s.headers.update({'User-Agent':ua.Chrome})
# response = s.get(url=urls)
# if response.status_code == 200:
#     response.encooding = response.apparent_encoding
#
#     etre = HTML(response.text)
#     appids = etre.xpath('//textarea[@class="J_dynamic_data"]/text()')
#     appid = appids[0]
#     a = json.loads(appid)
#     b = a["items"][0]["__data_param"]["appId"]
#
#     data = {"curPageUrl":urls,
#             "appId":b,
#             "bizId":99,
#             "terminalType":0,
#             "_pvuuid":"1560997920326",
#             "isbackup":"true",
#             "wh_pid":163144}
#
#     url = 'https://h5api.m.tmall.com/h5/mtop.tmall.kangaroo.core.service.route.aldlampservice/1.0/?jsv=2.4.16&appKey=12574478&t=1561010020005&sign=88069a3a344cb4c0ff3506b753ec0439&api=mtop.tmall.kangaroo.core.service.route.AldLampService&dataType=jsonp&v=1.0&timeout=2000&type=jsonp&callback=mtopjsonp2&data=%7B%22curPageUrl%22%3A%22https%253A%252F%252Fpages.tmall.com%252Fwow%252Fa%252Fact%252Ftmall%252Ftmc%252F22351%252Fwupr%253Fspm%253D875.7931836%252FB.category201661810.1.534942659mLBO5%2526wh_pid%253Dindustry-163162%2526acm%253Dlb-zebra-148799-983674.1003.4.6142250%2526scm%253D1003.4.lb-zebra-148799-983674.OTHER_0_6142250%22%2C%22appId%22%3A%224533132%22%2C%22bizId%22%3A99%2C%22terminalType%22%3A0%2C%22_pvuuid%22%3A%221561009994956%22%2C%22isbackup%22%3Atrue%2C%22wh_pid%22%3A163162%7D'
#     resp = s.get(url=url,params=data)
#
#     _m_h5_tk = resp.cookies["_m_h5_tk"]
#
#     print(_m_h5_tk)
#     # keyword = "女装"
#     # page = 2
#     datas = str(data)
#     _m_h5_tk = _m_h5_tk.split('_')[0]
#     times = str(int(time.time() * 1000))
#     sgin = str(_m_h5_tk) + "&" + times + "&" + "12574478" + "&" + str(data)
#     #
#     sign = hashlib.md5(str().encode('utf-8')).hexdigest()
#
#     urll = 'https://h5api.m.tmall.com/h5/mtop.tmall.kangaroo.core.service.route.aldlampservice/1.0/?jsv=2.4.16&appKey=12574478&t={}&sign={}&api=mtop.tmall.kangaroo.core.service.route.AldLampService&dataType=jsonp&v=1.0&timeout=2000&type=jsonp&callback=mtopjsonp6&data={}'.format(times,sign,data)
#     resps = s.get(url=urll)
#     s.headers.update({
#         'Referer': 'https://pages.tmall.com/wow/a/act/tmall/tmc/22351/wupr?spm=875.7931836/B.category201661812.1.659c42650pGCtU&wh_pid=industry-163144&acm=lb-zebra-148799-983674.1003.4.6142250&scm=1003.4.lb-zebra-148799-983674.OTHER_2_6142250'
#     })


url = 'https://www.tmall.com/'

resp = s.get(url=url)
if resp.status_code == 200:
    resp.encoding = resp.apparent_encoding
