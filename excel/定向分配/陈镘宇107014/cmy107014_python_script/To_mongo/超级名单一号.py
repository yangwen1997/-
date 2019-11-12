'''
@author     ：  yangwenlong
@file       :   ztl
@intro      :   陈镘宇107014存入monmgo
@creatime   :   2019/9/25
'''
import xlrd
import hashlib
from cmy107014_python_script.common import Enterprise_db,get_log

log = get_log()


#使用xlrd打开工作本（excel文件）
book = xlrd.open_workbook(r'D:\白名单\定向分配资源整理\excel\定向分配\陈镘宇107014\名单\超级名单一号(2).xls')

#使用已经打开的excel文件里面的sheet_by_index(0)方法来获取该excel的文档对象
sheet=book.sheet_by_index(0)


def save(item):
    item["_id"] = hashlib.md5(str(item["电话"]).encode('utf-8')).hexdigest()
    Enterprise_db.save(item)
    log.info("数据{}存入mongodb成功".format(item["电话"]))

# 循环ncols可以获取整列内容
# 循环获取每行的内容
for i in range(sheet.nrows):

    item = {}
    item["公司"] = sheet.row_values(i)[0]
    item["公司类型"] = sheet.row_values(i)[5]
    item["负责人姓名"] = None
    item["联络员姓名"] = None

    phone= str(sheet.row_values(i)[12])
    if phone == "" or not phone:
        phone = str(sheet.row_values(i)[13])

    item["经营范围"] = sheet.row_values(i)[10]
    item["地址"] = sheet.row_values(i)[8]
    item["法定代表人"] = sheet.row_values(i)[4]
    item["成立日期"] = sheet.row_values(i)[6]

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
