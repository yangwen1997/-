'''
@author     ：  yangwenlong
@file       :   ztl
@intro      :   张兵107631存入monmgo
@creatime   :   2019/10/8
'''
import xlrd
import hashlib
from zb_python_script.common import Enterprise_db,get_log,DB

log = get_log()

Individual_db = DB["DXTS"]["张兵107631-个人-邮政"]

#使用xlrd打开工作本（excel文件）
book = xlrd.open_workbook(r'D:\白名单\定向分配资源整理\excel\定向分配\张兵107631\邮政3.xlsx')

#使用已经打开的excel文件里面的sheet_by_index(0)方法来获取该excel的文档对象
sheet=book.sheet_by_index(0)


def save(item):
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
        item["姓名"] = sheet.row_values(i)[1]
        phone = str(sheet.row_values(i)[2])
        item["备注"] = sheet.row_values(i)[3]
        item["还款方式"] = sheet.row_values(i)[4]
        item["还款金额"] = sheet.row_values(i)[5]
        item["贷款起期"] = sheet.row_values(i)[6]
        item["担保物价值"] = sheet.row_values(i)[7]

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
