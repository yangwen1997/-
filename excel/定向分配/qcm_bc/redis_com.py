import redis
from common import get_log,db,Red_cli


log = get_log()

data = db.find({"redis": None})

for _ in data:
    item = {}
    item["公司"] = _["公司"]
    item["_id"] = _["_id"]
    item["电话"] = _["电话"]
    if item["公司"]:
        result = Red_cli.sadd("company_search",str(item))
        if result == 1:
            log.info("公司名存入redis成功")
