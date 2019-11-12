'''
@author     ：  yangwenlong
@file       :   ztl
@intro      :   陈镘宇107014存入monmgo
@creatime   :   2019/9/25
'''
import xlrd
import hashlib
import re
from cmy107014_python_script.common import Enterprise_db,get_log,DB
import json

log = get_log()

Individual_db = DB["DXTS"]["陈镘宇107014-个人-一米阳光"]

#使用xlrd打开工作本（excel文件）
book = xlrd.open_workbook(r'D:\白名单\定向分配资源整理\excel\定向分配\陈镘宇107014\名单\一米阳光.xlsx')

#使用已经打开的excel文件里面的sheet_by_index(0)方法来获取该excel的文档对象
sheet=book.sheet_by_index(1)


def save(item):
    jsonData = json.dumps(item["电话"])

    #替换中文和英文为空
    jsonData = re.sub(r'(\\u\d+)',"",jsonData)
    jsonData = re.sub(r'([a-z]+)',"",jsonData)
    json.loads(jsonData)

    item["电话"] = json.loads(jsonData)

    if item["电话"]:
        item["_id"] = hashlib.md5(str(item["电话"]).encode('utf-8')).hexdigest()
        Individual_db.save(item)
        log.info("数据{}存入mongodb成功".format(item["电话"]))

# 循环ncols可以获取整列内容
# 循环获取每行的内容
for i in range(sheet.nrows):
    if i == 0:
        continue
    else:
        item = {}
        item["房号"] = sheet.row_values(i)[0]
        item["面积"] = sheet.row_values(i)[1]
        item["姓名"] = sheet.row_values(i)[2]
        phone = str(sheet.row_values(i)[3])
        item["价格"] = sheet.row_values(i)[4]
        item["装修"] = sheet.row_values(i)[5]
        item["现状"] = sheet.row_values(i)[6]
        item["最新情况"] = sheet.row_values(i)[7]
        item["房源编号"] = sheet.row_values(i)[8]

        if "；" in phone:
            phone_lt = phone.split("；")
            for _ in phone_lt:
                if _ and _ != '':
                    if "." in _:
                        item["电话"] = _.split(".")[0]
                        save(item)
                    else:
                        item["电话"] = _
                        save(item)
        else:
            if phone:
                if "." in phone:
                    item["电话"] = phone.split(".")[0]
                    save(item)
                else:
                    item["电话"] = phone
                    save(item)
