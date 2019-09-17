'''
@author     :   yangwenlong
@file       :   mfcode_to_redis
@explain    :   从redis中获取公司名录进行生成mfcode参数
@time       :   2019/9/12
@info       :   拿到公司名录生成mfcode参数
'''
import asyncio
import aiohttp
import re
import time
import execjs
import redis
from common.commons import REDIS_COMPANY_NAME
from common.commons import REDIS_MFCODE_KEY
from common.commons import Red_cli
from commons import ABY_IP_
from easydict import EasyDict
from commons import get_log


log = get_log()
REDIS_MF = Red_cli
urls = "https://www.qichamao.com/home/GetJsVerfyCode"

class QCM_MFCODE(object):
    """
    企查猫生成mfcode类并存入本地monfodb
    """

    def __init__(self,process):
        """
        初始化类
        :param process: 协程名
        """
        self.process_name = process

    async def get_base_cookie(self,url, headers=None, cookie=None):
        """
        获取首页js
        :param url:
        :return:
        """
        proxies = ABY_IP_()

        async with aiohttp.ClientSession() as session:
            if "https" not in url:
                async with session.get(url, proxy=proxies["http"], timeout=10)as resp:
                    cookie = resp.headers["Set-Cookie"]
                    resp.encodng = "utf-8"
                    resp = await resp.text()
            else:
                async with session.get(url,proxy=proxies["https"], timeout=10)as resp:

                    cookie = resp.headers["Set-Cookie"]
                    resp.encodng = "utf-8"
                    resp = await resp.text()
            return cookie, resp

    async def get_req(self,url:str, headers=None, cookie=None):
        """
        发起get请求
        :param url:
        :return:
        """
        proxies = ABY_IP_()

        async with aiohttp.ClientSession(headers=headers) as session:
            if "https" not in url:
                async with session.get(url, proxy=proxies["http"], timeout=10)as resp:
                    resp.encodng = "utf-8"
                    resp = await resp.text()
            else:
                async with session.get(url,proxy=proxies["https"], timeout=10)as resp:
                    resp.encodng = "utf-8"
                    resp = await resp.text()
            return resp

    async def run(self):
        log.info("当前程序为{}号协程".format(self.process_name))

        cookie, result = await self.get_base_cookie(urls)
        # 解析出qznewsite.uid和mfcode的js参数
        cook = cookie.split(";")[0]
        mfjs = result.replace(";w[s([95,95,113,122,109,99,102])]=dc})(window);", "").replace("(function(w){", "")
        cookjs = mfjs.replace("w.document[s([99,111,111,107,105,101])].split('; ')", "['{}']".format(cook))
        etx = execjs.compile(cookjs)
        mfcode = etx.call("dc")

        company = REDIS_MF.srandmember(REDIS_COMPANY_NAME)

        item = eval(company)
        item["cookie"] = cookie
        item["mfcode"] = mfcode

        state = REDIS_MF.sadd(REDIS_MFCODE_KEY, str(item))
        if state == 1:
            log.info("数据存入redis成功状态为{}".format(state))
            Red_cli.srem(REDIS_COMPANY_NAME,company)
        else:
            log.info("数据存入redis失败状态为{}".format(state))

async def do_some_work(x):
    """
    如果mfcode数据中的数据小于1000则自动推送名录
    :param x:
    :return:
    """
    while True:
        count = Red_cli.scard(REDIS_MFCODE_KEY)
        if count < 10000:
            start = QCM_MFCODE(x)
            await start.run()
        else:
            time.sleep(3)

async def start():

    # count = REDIS_MF.scard(REDIS_COMPANY_NAME)

    while True:


        #创建任务执行初始函数
        coroutine = [do_some_work(_) for _ in range(1,11)]

        #添加任务到队列
        tasks = [
            asyncio.ensure_future(_)for _ in coroutine
        ]

        #挂载任务执行
        await asyncio.wait(tasks)




def main():
    #创建协程io事件循环
    loop = asyncio.get_event_loop()
    #执行放进队列中执行任务
    loop.run_until_complete(start())

if __name__ == '__main__':
    main()
