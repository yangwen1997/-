'''
@author     ：  yangwenlong
@file       :   zss_1500
@intro      :   张珊珊1500条资源存入monmgo
@creatime   :   2019/9/25
'''
import xlrd
import hashlib
from python_script.common import Enterprise_db,get_log

log = get_log()


#使用xlrd打开工作本（excel文件）
book = xlrd.open_workbook('D:\白名单\定向分配资源整理\excel\定向分配\张珊珊959191597\张珊珊1500.xlsx')

#使用已经打开的excel文件里面的sheet_by_index(0)方法来获取该excel的文档对象
sheet=book.sheet_by_index(0)


# 循环ncols可以获取整列内容
# 循环获取每行的内容
for i in range(sheet.nrows):
    item = {}
    if i == 0:
        continue
    else:
        item["公司"] = sheet.row_values(i)[0]
        item["姓名"] = sheet.row_values(i)[1]
        item["电话"] = sheet.row_values(i)[2]
        item["地址"] = None

        if item["电话"]:
            item["_id"] = hashlib.md5(str(item["电话"]).encode('utf-8')).hexdigest()
            Enterprise_db.save(item)
            log.info("数据{}存入mongodb成功".format(item["电话"]))
