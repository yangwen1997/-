
import redis
import pymongo
from setting import MONGO_DC, MONGO_DA, MONGO_DE
from spider.mongo import MongoDB
import cpca




class TransAddr(object):
    def __init__(self):
        self.redis = redis.Redis(host='127.0.0.1', port=6379, db=5)
        self.mc = MONGO_DC
        self.db = MONGO_DA
        self.col = MONGO_DE
        self.mongodb = pymongo.MongoClient(self.mc)[MONGO_DA][MONGO_DE]

    def get_addr(self):
        try:
            info = self.redis.spop('Address')
            if info == None:
                print('数据库无数据')
                return False
            else:
                info = eval(info.decode(encoding="utf-8"))
                return info
        except Exception as e:
            print(e, '从数据库获取地址失败')

    def trans(self):
        addr_info = self.get_addr()
        if addr_info is not False:
            _id = addr_info['_id']
            addr = addr_info['companyAddr']
            if addr != '':
                location_str = [addr]
                df = cpca.transform(location_str)
                pro = list(df['省'])[0]
                if pro == '':
                    pro = None
                city = list(df['市'])[0]
                if city == '':
                    city = None
                item = {'_id': _id, 'pro': pro, 'city': city}
                return item
            else:
                print('该公司地址为空，不检测')
        else:
            return False

    def update_Mongo_addr(self, item):
        try:
            _id = item['_id']
            pro = item['pro']
            city = item['city']
            self.mongodb.update_one({'_id': _id}, {'$set': {'companyProvince': pro, 'companyCity': city}})
        except Exception as e:
            print(e)

    def run(self):
        while True:
            item = self.trans()
            if item is False:
                break
            self.update_Mongo_addr(item)


def get_addr_to_redis(MONGO_MC, MONGO_DA, MONGO_DE):
    """从mongo数据库中取出电话号码，存入redis"""
    db = MongoDB(uri=MONGO_MC,db=MONGO_DA,collection=MONGO_DE)
    # redis_db = redis.Redis(host='10.0.0.55', port='6379', db=2, password="dgg962540")
    redis_db = redis.Redis(host='127.0.0.1', port='6379', db=5)
    # db = self.mongodb
    data = db.mongo_find_one()
    # print(data)
    # for i in data:
    _id = data['_id']
    companyName = data['companyName']
    companyAddr = data['companyAddr']
    if companyAddr != '':
        redis_db.sadd('Address', str({'_id': _id, 'companyName': companyName, 'companyAddr': companyAddr}))
        print('数据插入redis成功')
    else:
        print('该公司地址为空')

if __name__ == '__main__':
    a = TransAddr()
    a.run()
    # get_addr_to_redis(MONGO_MC=MONGO_DC, MONGO_DA=MONGO_DA, MONGO_DE=MONGO_DE)
