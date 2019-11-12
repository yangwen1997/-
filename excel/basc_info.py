from user_portrayal.common import basic_db,get_log
from sq_144.storage_mysql import Storage


mongo_datas = basic_db.find({})
log = get_log()

for mongo_data in mongo_datas:
    sql = "insert into basic_info(_id, companyName, legalMan, registerMoney, registerTime, creditCode, registerAddress, companyProvince, businessScope, companyUrl, companyWebeUrl, customer_id, business_id) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(mongo_data["_id"], mongo_data["companyName"], mongo_data["legalMan"], mongo_data["registerMoney"], mongo_data["registerTime"], mongo_data["creditCode"], mongo_data["registerAddress"], mongo_data["companyProvince"], mongo_data["businessScope"], mongo_data["companyUrl"], mongo_data["companyWebeUrl"], mongo_data["customer_id"], mongo_data["business_id"])
    Storage().run_sql(sql)
    log.info("数据存入144服务器mysql成功，sql语句为-{}".format(sql))
