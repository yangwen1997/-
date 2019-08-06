# author 杨文龙

import threadpool
import asyncio
import multiprocessing
# from qcc_spider.qcc import QCC
from qcc_spider.upqib import QCC

def func(*args):
    """
    爬取准备
    :param args:
    :return:
    """
    tz = QCC()
    tz.run()

def pro():
    """
    使用进程
    :return:
    """

    #开启的进程个数
    pool = multiprocessing.Pool(processes=2)

    for i in range(1):
        pool.apply_async(func)

    pool.close()
    pool.join()

def thr():
    """
    使用线程
    :return:
    """
    pool = threadpool.ThreadPool(10)
    name_list = ['1','2','3','4','5','6']
    res = threadpool.makeRequests(func,name_list)
    [pool.putRequest(req) for req in res]
    pool.wait()

def main():
    """
    程序入口函数
    :return:
    """
    pro()
    # thr()

if __name__ == '__main__':
    main()