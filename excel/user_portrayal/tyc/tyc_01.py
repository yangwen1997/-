#!/usr/bin/env Python
# coding=utf-8
import asyncio
import hashlib
import multiprocessing
from user_portrayal.common import get_log,conn,cursor,tyc_db,red_cli
from middleware import parse_addr,SQL_insert
log = get_log()

class data_dispose(object):

    def __init__(self):
        pass

    @staticmethod
    def replace_items(items):
        data_item = {}
        for k,v in items.items():
            data_item[k] = v.replace("〓","").replace("\x00","").replace("\t","").replace("\u0000","")

        return data_item

    @staticmethod
    def data_change(data):
        """
        转换数据为sql中的格式
        :return:
        """
        TAG = 1
        items = {}
        items["_id"] = hashlib.md5(str(data["companyName"]).encode('utf-8')).hexdigest()
        try:
            items["companyName"] = data["companyName"]
            items["legalMan"] = data["docs"]["background"]["baseInfo"]["legalMan"]
            items["registerMoney"] = data["docs"]["background"]["baseInfo"]["registerMoney"]
            items["registerTime"] = data["docs"]["background"]["baseInfo"]["registerTime"]
            items["companyTel"] = data["docs"]["background"]["baseInfo"]["companyTel"]

            items["registerAddress"] = data["docs"]["background"]["baseInfo"]["registerAddress"]
            items["companyWebeUrl"] = data["docs"]["background"]["baseInfo"]["companyWebeUrl"]
            items["companyEmail"] = data["docs"]["background"]["baseInfo"]["companyEmail"]

            items["businessScope"] = data["docs"]["background"]["baseInfo"]["businessScope"]
            items["creditCode"] = data["docs"]["background"]["baseInfo"]["creditCode"]



        except Exception as e:
            TAG = 2
            err_count = red_cli.scard("tyc_err")
            if err_count < 10000:
                error_item = {}
                error_item["_id"] = items["_id"]
                error_item["companyName"] = items["companyName"]
                error_item["errorMsg"] = str(e)
                err_result = red_cli.sadd("tyc_err",str(error_item))
                log.info("数据解析异常插入redis状态为{}".format(err_result))
            else:
                exit()
        if TAG != 2:
            companyProvince, companyCity, area = parse_addr(items["registerAddress"], items["companyName"])
            items["companyProvince"] = companyProvince
            items["companyCity"] = companyCity
            items["area"] = area

            replace_end_items = data_dispose().replace_items(items)

            sql = "insert into tyc_basic_info_1(_id,companyName,legalMan,registerMoney,registerTime,companyTel,registerAddress,companyWebeUrl,companyEmail,businessScope,creditCode,companyProvince,companyCity,area) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(replace_end_items["_id"],replace_end_items["companyName"],replace_end_items["legalMan"],replace_end_items["registerMoney"],replace_end_items["registerTime"],replace_end_items["companyTel"],replace_end_items["registerAddress"],replace_end_items["companyWebeUrl"],replace_end_items["companyEmail"],replace_end_items["businessScope"],replace_end_items["creditCode"],replace_end_items["companyProvince"],replace_end_items["companyCity"],replace_end_items["area"])
            # print(sql)
            # cursor.execute(sql)
            # print("**")
            SQL_insert(sql,conn,cursor,log)
            # return replace_end_items
        return True

async def do_work(x,errors='ignore'):
    """
    程序入口函数
    :return:
    """

    #2千万存一张表 limit 读取数据的条数 skip 偏移量
    # results = tyc_db.find({}).limit(20000000).skip(988575)
    # results = tyc_db.find({}).limit(270002).skip(270000)
    count = red_cli.scard("tyc_id_red")
    if count > 0:
        keys = red_cli.srandmember("tyc_id_red")
        results = tyc_db.find_one({"_id":eval(keys)["_id"]})

        # count = 20000000 - 280000
        # for _ in results:
        try:
            res = results["docs"]["background"]["baseInfo"]["legalMan"]

            log.info("当前redis没有存入服务器数据数量{}".format(str(count)))
            DATA_TAG = data_dispose().data_change(results)
            if DATA_TAG:
                red_cli.srem("tyc_id_red",keys)
        except Exception as e:
            if str(e) == "'legalMan'":
                red_cli.srem("tyc_id_red", keys)
                log.info("数据异常已删除。。。。。。。。。。。。。")
    else:
        exit()


async def asy(errors='ignore'):

    while True:

        #创建任务执行初始函数
        coroutine = [do_work(_) for _ in range(1,21)]
        #添加任务到队列
        tasks = [ asyncio.ensure_future(_)for _ in coroutine ]
        #挂载任务执行
        await asyncio.wait(tasks)

def main():

    # 创建协程io事件循环
    loop = asyncio.get_event_loop()
    # 执行放进队列中执行任务
    loop.run_until_complete(asy())

if __name__ == '__main__':
    # 开启的进程个数
    pool = multiprocessing.Pool(processes=21)

    for i in range(21):
        pool.apply_async(main)

    pool.close()
    pool.join()


