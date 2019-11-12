from user_portrayal.common import get_log,tyc_db,red_cli

log = get_log()

results = tyc_db.find({}).limit(15000000).skip(10000000)
# results = tyc_db.find({}).limit(988577).skip(988575)


for _ in results:
    try:
        redis_item = {}
        redis_item["_id"] = _["_id"]
        result = red_cli.sadd("tyc_id_red",str(redis_item))
        log.info("数据存入redis状态为{}".format(result))
    except Exception as e:
        print(e)
