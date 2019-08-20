# -*- coding: utf-8 -*-
import pymongo
import time
import requests



# 重新拨号
def redail_ip(mac, port):
    print(mac)
    # 调用重新拨号的API
    while True:
        retry_response = requests.get("http://10.0.0.55:{}/redail/{}".format(port, mac)).text
        # 重新拨号成功
        if 'ack' in retry_response:
            print('sleep 5s')
            time.sleep(5)
            # 调用获取IP的API获取新IP
            count = 1
            while True:
                response1 = requests.get("http://10.0.0.55:{}".format(port)).json()
                if response1:
                    new_ip = response1.get(mac)
                    # ip已经更新
                    if new_ip:
                        return new_ip
                    # IP还有更新完成
                    else:
                        if not count % 30:
                            error_message = 'Vps is error'
                            print(error_message)
                            count += 1
                            quit()
                        print('IP had not update, time sleep 3s...')
                        time.sleep(3)
                        count +=1
                        continue
                else:
                    print('API return empty, time sleep 10s...')
                    time.sleep(10)
                    continue
        elif "Keep trying" in retry_response:
            print(retry_response)
            return
        else:
            error_message = 'dial failed, error: {}'.format(retry_response)
            print(error_message)
            quit()


def add_new_ip(collection, bad_collection, port):
    '''
    功能：添加静态IP
    :param collection: vps_static_ip_results:当作静态IP来用的, back_ip_results:当作拨号IP的库
    :param bad_collection: bad_ip_results:记录已经出现过的IP
    :param port: 服务端获取IP的端口号
    :param log: 日志类
    :return:
    '''
    # ip_lists里面是否有数据
    all_res = collection.find({'port': port}).count()
    response = requests.get("http://10.0.0.55:{}".format(port)).json()
    # response = requests.get("http://10.0.0.55:10002").json()
    if all_res >= len(response):
        # 没有新数据，跳过
        print('not add new IP')
    else:
        # 没有数据或者有新数据，新增
        # 调用获取IP的API获取全部ip
        for mac, ip in response.items():
            time.sleep(1)
            mac_res = collection.find_one({'mac': mac})
            if mac_res:
                continue
            else:
                print('mac:[{}]  ip:[{}]'.format(mac, ip))
                while True:
                    # 检查是否是已经出现过的IP
                    old_res1 = bad_collection.find_one({'ip': ip})
                    if old_res1:
                        # IP已经重复出现次数+1
                        bad_collection.update_one({'_id': old_res1.get('_id')}, {'$set': {'bad_count': old_res1.get('bad_count') + 1}})
                        # 重新拨号
                        ip = redail_ip(mac, port)
                        continue
                    else:
                        # 新IP添加到历史库，重复出现次数为0
                        bad_collection.insert_one({'ip': ip, 'bad_count': 0})
                        # IP没有出现过，新增
                        collection.insert_one({'mac': mac, 'ip': ip, 'flag': True, 'updateTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'port': port})
                        break

if __name__ == '__main__':

    """mongo配置"""
    client = pymongo.MongoClient("mongodb://root:root962540@10.0.0.55:27017")
    db = client['ip_db']
    ip_collection = db['ip_results']
    back_ip_collection = db['back_ip_results']
    vps_static_ip_collection = db['vps_static_ip_results']
    hui_ip_collection = db['hui_ip_results']
    bad_ip_collection = db['bad_ip_results']
    """--------"""
    # 动态IP的端口
    port = [10002, 10003, 10004, 10005, 10006]
    # 静态IP的端口
    static_port = [10002]
    for _ in port:
        print('port is ：{}'.format(_))
        if _ in static_port:
            # 添加静态IP
            add_new_ip(vps_static_ip_collection, bad_ip_collection, _)
        else:
            # 添加动态IP
            time.sleep(10)
            add_new_ip(back_ip_collection, bad_ip_collection, _)

    # 将动态IP添加到IP池中
    back_res = back_ip_collection.find({})
    print('dynamic IP total is ：{}'.format(back_res.count()))
    for _ in back_res:
        res = ip_collection.find_one({'mac': _.get('mac')})
        if res:
            continue
        else:
            ip_collection.insert_one({
                'mac': _.get('mac'),
                'ip': _.get('ip'),
                'updateTime': _.get('updateTime'),
            })

    while True:
        for _ in port:
            print('port is ：{}'.format(_))
            if _ in static_port:
                # 添加静态IP
                add_new_ip(vps_static_ip_collection, bad_ip_collection, _)
            else:
                # 添加动态IP
                add_new_ip(back_ip_collection, bad_ip_collection, _)

        res = ip_collection.find({}).sort('updateTime', pymongo.ASCENDING)
        count = 0
        for _ in res:
            if count < 10:
                now_time = time.time()
                update_time = time.mktime(time.strptime(_.get('updateTime'), "%Y-%m-%d %H:%M:%S"))
                if int(now_time)-int(update_time) > 60:
                    back = back_ip_collection.find_one({'mac': _.get('mac')})
                    if back.get('flag'):
                        back_ip_collection.update_one({'mac': _.get('mac')}, {'$set': {'flag': False}})
                        count += 1
            else:
                break
        print('sleep 20')
        time.sleep(20)
