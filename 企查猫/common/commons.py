"""
公共文件
"""

import logging

import pymongo
import redis
import os
import time
from mongo import MongoDB

#redis
Red_cli = redis.Redis(host="127.0.0.1",port=6379, db=10)


#阿布云代理
def ABY_IP_():
    """#
    阿布云代理接入
    :return:
    """
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "H8DKHJ178U226QAD"
    proxyPass = "869B28FDC6B3BA53"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    return proxies



def logger(FILE_NAME):
    """
    日志配置
    :param FILE_NAME: 日志文件名(全路径 )
    :return:日志记录生成器
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%Y %H:%M:%S',
        filename=FILE_NAME,
        filemode='w'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(filename)s[Line:%(lineno)d] [%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    return logging

def get_log():
    real_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + "/log/"
    file_name = "{}_qcm_{}.log".format(real_path,
                                             time.strftime("%Y-%m-%d",
                                                           time.localtime()))

    log = logger(file_name)
    return log



# redis地址 公司名录库  mfcode库
REDIS_COMPANY_NAME = "qcm_keys"
REDIS_MFCODE_KEY = "mfcode_name"

#mongodb地址  MongoDB('127.0.0.1:27017', 'test', 'test_coll')
db = MongoDB('mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017', 'all_com_wash', 'qcm_Guangdong')



#没有搜索到公司时回写的mongo地址
DB = pymongo.MongoClient("mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017")
error_db = DB["all_com_wash"]["Guangdong"]