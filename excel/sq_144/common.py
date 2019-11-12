import pymysql
import pymongo
import logging
import time
import os

#mongo地址
MON_DB = pymongo.MongoClient("mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017")
m_db = MON_DB["qixin_com"]["complete_order"]
#基本信息
basic_db =  MON_DB["User_portrait"]["basic_info"]

#mysql地址
conn = pymysql.Connect(host="192.168.254.144", user="root", password="root",database="YWL", port=3306)
cursor = conn.cursor()


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
    file_name = "{}_数据分表_{}.log".format(real_path,
                                             time.strftime("%Y-%m-%d",
                                                           time.localtime()))

    log = logger(file_name)
    return log

