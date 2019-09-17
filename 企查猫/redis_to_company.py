'''
@author :   yangwenlong
@file   :   redis_to_company
@explain:   从mongo获取名录写入redis
@time   :   2019/9/12
@info   :   从mongo中获取抓取完毕的公司名录存入redis,存入成功回写mongodb中数据增加redis为1的字段做标志
'''
from commons import Red_cli
import pymongo
from easydict import EasyDict

item = EasyDict()

DB = pymongo.MongoClient("mongodb://rwuser:48bb67d7996f327b@10.2.1.216:57017,10.2.1.217:57017,10.2.1.218:57017")
db = DB["all_com_wash"]["Guangdong"]
# log = get_log()

data = db.find({"flag" : 1, "mark": 1})

for _ in data:
    item._id = _["_id"]
    item.companyName = _["companyName"]
    item.outName = _["outName"]
    item.companyTel = _["companyTel"]
    item.companyUrl = _["companyUrl"]
    item.companyAddr = _["companyAddr"]
    item.companyCity = _["companyCity"]
    item.companyProvince = _["companyProvince"]
    item.websource = _["websource"]
    item.flag = _["flag"]
    item.mark = _["mark"]
    result = Red_cli.sadd("qcm_keys",str(item))
    if result == 1:
        print("数据存入成功")
        db.find_one_and_update({"_id":_["_id"]},{"$set":{"redis":1}})
    else:
        print("数据存入失败")