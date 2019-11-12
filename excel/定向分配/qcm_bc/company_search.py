import asyncio
import aiohttp
import time
import execjs
import json
from common import ABY_IP_,get_log,db,dbb,Red_cli
from lxml.etree import HTML
from easydict import EasyDict
from xpath_base import XPATH
log = get_log()



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

def result_filter(result: list):
    if result:
        result = result[0].replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "").replace("\x00", "")
        return result
    result = ""
    return result

async def get_base_cookie(url, headers=None, cookie=None):
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
            async with session.get(url, proxy=proxies["https"], timeout=10)as resp:

                cookie = resp.headers["Set-Cookie"]
                resp.encodng = "utf-8"
                resp = await resp.text()
        return cookie, resp

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

            item.companyAddr = "".join(etre.xpath('//div[@class="arthd_info"]/*[contains(text(),"企业地址")]/text()')).replace("企业地址：","")

            #解析基本信息
            base = EasyDict()
            qcm_xpath = XPATH()
            #邮箱  统一社会信用代码 注册号 机构代码 法定代表人 企业类型 经营状态 注册资本
            base.companyEmail = result_filter([_ for _ in etre.xpath(qcm_xpath.companyEmail) if etre.xpath(qcm_xpath.companyEmail)!= []])
            base.creditCode = result_filter([_ for _ in etre.xpath(qcm_xpath.creditCode) if etre.xpath(qcm_xpath.creditCode)])
            base.registerNum = result_filter([_ for _ in etre.xpath(qcm_xpath.registerNum) if etre.xpath(qcm_xpath.registerNum)])
            base.OrganizationCode = result_filter([_ for _ in etre.xpath(qcm_xpath.OrganizationCode) if etre.xpath(qcm_xpath.OrganizationCode)])
            base.legalMan = result_filter([_ for _ in etre.xpath(qcm_xpath.legalMan) if etre.xpath(qcm_xpath.legalMan)])
            base.companyType = result_filter([_ for _ in etre.xpath(qcm_xpath.companyType) if etre.xpath(qcm_xpath.companyType)])
            base.businessState = result_filter([_ for _ in etre.xpath(qcm_xpath.businessState) if etre.xpath(qcm_xpath.businessState)])
            base.registerMoney = result_filter([_ for _ in etre.xpath(qcm_xpath.registerMoney) if etre.xpath(qcm_xpath.registerMoney)])

            #成立日期  登记机关 经营期限 所属地区 核准日期 经营范围
            base.registerTime = result_filter([_ for _ in etre.xpath(qcm_xpath.registerTime) if etre.xpath(qcm_xpath.registerTime)])
            base.registOrgan = result_filter([_ for _ in etre.xpath(qcm_xpath.registOrgan) if etre.xpath(qcm_xpath.registOrgan)])
            base.operating_period = result_filter([_ for _ in etre.xpath(qcm_xpath.operating_period) if etre.xpath(qcm_xpath.operating_period)])
            base.area = result_filter([_ for _ in etre.xpath(qcm_xpath.area) if etre.xpath(qcm_xpath.area)!= []])
            base.approval_time = result_filter([_ for _ in etre.xpath(qcm_xpath.approval_time) if etre.xpath(qcm_xpath.approval_time)!= []])
            base.scope = result_filter([_ for _ in etre.xpath(qcm_xpath.scope) if etre.xpath(qcm_xpath.scope)!= []])
            item.base = base


            #变更信息
            changeInfo = EasyDict()
            changeInfo.changeInfoCount = result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfoCount) if etre.xpath(qcm_xpath.changeInfoCount)!= []])
            changeInfo.changeInfo_project = result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_project) if etre.xpath(qcm_xpath.changeInfo_project)!= []])
            changeInfo.changeInfo_after = result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_after) if etre.xpath(qcm_xpath.changeInfo_after)!= []])
            changeInfo.changeInfo_end = result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_end) if etre.xpath(qcm_xpath.changeInfo_end)!= []])
            changeInfo.changeInfo_time = result_filter([_ for _ in etre.xpath(qcm_xpath.changeInfo_time) if etre.xpath(qcm_xpath.changeInfo_time)!= []])
            item.changeInfo = changeInfo
            print(item)
            break
        except Exception as e:
            print(e)
            if str(e) == "list index out of range":
                time.sleep(10)

async def get_req(session,url):
    """
    :param session:  aiohttp的session对象
    :param url:     请求的网址
    :return: 返回请求的文本信息
    """
    proxy = ABY_IP_()
    async with session.get(url, proxy=proxy["https"])as resp:
        result = await resp.text(encoding='utf-8')
        return result

async def post_req(session,url,post_parmas):
    proxy = ABY_IP_()
    async with session.post(url,data=post_parmas, proxy=proxy["https"])as resp:
        result = await resp.text(encoding='utf-8')
        return result

async def do_some_work(x):
    """
    如果mfcode数据中的数据小于1000则自动推送名录
    :param x:
    :return:
    """
    # print("执行任务")
    count = Red_cli.scard("company_search")
    while count:
        try:
            data = Red_cli.srandmember('company_search')
            keys = eval(data)["公司"]
            if ":" in keys:
                keys = keys.split(":")[0]

            cookie, result = await get_base_cookie(url="https://www.qichamao.com/home/GetJsVerfyCode")
            # 解析出qznewsite.uid和mfcode的js参数
            cook = cookie.split(";")[0]
            mfjs = result.replace(";w[s([95,95,113,122,109,99,102])]=dc})(window);", "").replace("(function(w){", "")
            cookjs = mfjs.replace("w.document[s([99,111,111,107,105,101])].split('; ')", "['{}']".format(cook))
            etx = execjs.compile(cookjs)
            mfcode = etx.call("dc")

            urls = "https://www.qichamao.com/search/all/{}?o=0&area=0&mfccode={}"
            url = urls.format(keys, mfcode)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                "Cookie": cookie,
            }

            async with aiohttp.ClientSession(headers=headers)as session:
                result = await get_req(session,url)
                info_url = base_parse(result)

                if info_url:
                    response = await get_req(session,info_url)
                    if response:
                        item = EasyDict()
                        parse_base_info(response,item)
                        item._id = eval(data)["_id"]
                        item.companyName = eval(data)["公司"]
                        item.companyTel = eval(data)["电话"]
                        item.qcm_url = info_url

                        #获取商标数量
                        orgCode = info_url.split("/")[-1].split(".")[0]
                        post_parmas = {
                            "orgCode": orgCode,
                            "page": "1",
                            "pagesize": "5",
                            "datacount": "0",
                        }
                        sb_result = await post_req(session,"https://www.qichamao.com/orgcompany/brandlistbycode",post_parmas)
                        res = json.loads(sb_result)
                        item.brandCount = res["rowCount"]
                        try:
                            dbb.save(item)
                            db.find_one_and_update({"_id":item._id},{"$set":{"redis":10}})
                            Red_cli.srem("company_search",data)
                            count -= 1
                        except:
                            log.info("回写mongo出错")
                        log.info("数据回写到mongo中的redis为10")

                else:
                    #当搜索失败时逻辑
                    log.info("解析的公司详情url为空，检测是否搜索到公司")
                    etre = HTML(result)
                    try:
                        judge = "".join(etre.xpath('//em[@class="keyword SearchCompanyCount"]/text()'))
                        if judge:
                            if judge == '0':
                                _id = eval(data)["_id"]
                                db.find_one_and_update({"_id": _id}, {"$set": {"redis": 2}})
                                Red_cli.srem("company_search", data)
                                count -= 1
                                log.info('搜索到0家公司，回写Mongo中该数据的redis值为2')
                        else:
                            log.info('mfcode失效请重新获取名录')

                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

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
    # 创建协程io事件循环
    loop = asyncio.get_event_loop()
    # 执行放进队列中执行任务
    loop.run_until_complete(start())

if __name__ == '__main__':
    main()
