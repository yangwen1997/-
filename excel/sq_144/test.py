#encoding=utf8

from sq_144.common import conn,cursor,get_log
log = get_log()

from middleware import tradeClass,SQL_search,SQL_insert

# a = tradeClass("卫生")
sql = "select _id,trade from basic_info;"

result = SQL_search(sql,conn,cursor,log)

for _ in result:
    _id = _[0]
    _trade = _[1]
    result = tradeClass(_trade).run()
    sql_1 = "update gsjbxx set companyClass='{}' where _id ='{}';".format(result,_id)
    SQL_insert(sql_1,conn,cursor,log)
