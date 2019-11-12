from user_portrayal.common import cursor,conn
from user_portrayal.common import get_log
# import cpca
#
#
# # mongo_datas = m_db.find({})
# log = get_log()
# sql = "select companyName, _id, registerAddress from basic_info;"
# try:
#     cursor.execute(sql)
#     mongo_datas = cursor.fetchall()
#     conn.commit()
# except Exception as e:
#     conn.rollback()
#     print(e)
#
#
# def parse_addr(addr):
#     """
#     解析地址
#     :param addr:
#     :return:
#     """
#     try:
#         result = cpca.transform([addr])
#         companyProvince = result["省"][0]
#         companyCity = result["市"][0]
#         area = result["区"][0]
#     except:
#         companyProvince = ""
#         companyCity = ""
#         area = ""
#
#     return companyProvince, companyCity, area
#
# def run_sql(sql):
#     """
#     运行sql
#     :param sql:
#     :return:
#     """
#     try:
#
#         # print(sql)
#         cursor.execute(sql)
#         conn.commit()
#         log.info("更新成功，sql语句为--{}".format(sql))
#     except Exception as e:
#         conn.rollback()
#         print(e)
#
# for mongo_data in mongo_datas:
#     addr = mongo_data[2]
#
#     _id = mongo_data[1]
#     if addr:
#         companyProvince, companyCity, area = parse_addr(addr)
#         sql = "update basic_info set companyProvince='{}', companyCity ='{}',area ='{}' where _id='{}';".format(companyProvince,companyCity, area, _id)
#         run_sql(sql)
#     else:
#         addr = mongo_data[0]
#         companyProvince, companyCity, area = parse_addr(addr)
#         sql = "update basic_info set companyProvince='{}', companyCity ='{}',area ='{}' where _id='{}';".format(companyProvince,companyCity, area, _id)
#         run_sql(sql)


# from user_portrayal.common import cursor,conn
#
# sql = "show databases;"
# a = cursor.execute(sql)
# print(a)
#

