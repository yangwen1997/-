import asyncio
import aiohttp
import redis
from commons import ABY_IP_
from lxml.etree import HTML
red = redis.Redis(host="127.0.0.1",port=6379,db=10)
from easydict import EasyDict

urls = "https://www.qichamao.com/search/all/{}?o=0&area=0&mfccode={}"
# log = get_log()

def base_parse(result):
    """
    解析基本信息
    :return:
    """
    etree = HTML(result)
    url_lt = etree.xpath('//a[@class="listsec_tit"]/@href')
    if url_lt:
        url = "https://www.qichamao.com" + url_lt[0]
        return url

async def task(x):
    data = red.srandmember("mfcode_name")
    mfcode = eval(data)["mfcode"]
    keys = eval(data)["company"]
    cookie = eval(data)["cookie"]
    proxy = ABY_IP_()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        "Cookie" : cookie,
    }
    url = urls.format(keys,mfcode)
    print(url)
    async with aiohttp.ClientSession(headers=headers)as session:
        async with session.get(url,proxy=proxy["https"])as resp:
            result = await resp.text()

            item = EasyDict()
            info_url = base_parse(result)
            if info_url:
                proxy = ABY_IP_()
                async with session.get(info_url,proxy=proxy["https"])as response:
                    print(await response.text())

            else:
                print("未搜索到公司")


async def start():
    coroutine = [task(_) for _ in range(1)]
    tasks = [asyncio.ensure_future(_) for _ in coroutine]
    await asyncio.wait(tasks)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())

if __name__ == '__main__':
    main()