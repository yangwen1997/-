#encoding='utg-8'
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
book = xlrd.open_workbook(r'D:\白名单\定向分配资源整理\excel\定向分配\陈镘宇107014\名单\陈镘宇107014-白名单.xlsx')

#使用已经打开的excel文件里面的sheet_by_index(0)方法来获取该excel的文档对象
sheet=book.sheet_by_index(0)


def save(item):
    item["电话"] = item["电话"].strip(',；').replace("\xa0","")
    item["_id"] = hashlib.md5(str(item["电话"]).encode('utf-8')).hexdigest()
    if item["电话"]:
        Enterprise_db.save(item)
        log.info("数据{}存入mongodb成功".format(item["电话"]))

# 循环ncols可以获取整列内容
# 循环获取每行的内容
for i in range(sheet.nrows):
    if i != 0:
        item = {}
        item["公司"] = sheet.row_values(i)[8]
        item["法定代表人"] = sheet.row_values(i)[9]
        item["负责人姓名"] = sheet.row_values(i)[10]
        item["联络员姓名"] = sheet.row_values(i)[11]
        item["成立日期"] = sheet.row_values(i)[12]
        item["经营范围"] = sheet.row_values(i)[13]
        item["地址"] = sheet.row_values(i)[14]
        item["公司类型"] = sheet.row_values(i)[15]

        phone= str(sheet.row_values(i)[16])
        tal = str(sheet.row_values(i)[17])

        lts = []
        lt = []
        if phone:
            if "；" in phone:
                lts = phone.split('；')
            else:
                lts.append(phone)



        if tal:
            if "；" in tal:
                lt = tal.split('；')
            else:
                lt.append(tal)
        if len(lts)>0:
            for _ in lts:
                if "." in _:
                    item["电话"] = _.split(".")[0]
                    save(item)
                else:
                    item["电话"] = _
                    save(item)
        if len(lt)>0:
            for _ in lt:
                if "." in _:
                    item["电话"] = _.split(".")[0]
                    save(item)
                else:
                    item["电话"] = _
                    save(item)


