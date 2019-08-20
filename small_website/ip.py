# -*- coding: utf-8 -*-
import time
import requests
import pymongo
import threading


# 重新拨号
def redail_ip(mac, port, db):
    # print(mac)
    # 调用重新拨号的API
    while True:
        retry_response = requests.get("http://10.0.0.55:{}/redail/{}".format(port, mac)).text
        # 重新拨号成功
        if 'ack' in retry_response:
            # 删除IP池中需要去拨号的IP
            db['ip_results'].delete_one({'mac': mac})
            # print('sleep 5s')
            # time.sleep(5)
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
                        if not count % 10:
                            error_message = 'Vps is error'
                            print(error_message)
                            count += 1
                            quit()
                        # print('IP还有更新完成, 5s后重新获取...')
                        time.sleep(5)
                        count +=1
                        continue
                else:
                    print('API return empty, time sleep 10s...')
                    time.sleep(10)
                    continue
        elif "Keep trying" in retry_response:
            print(retry_response)
            print('[port]: {} [mac]: {} [error]: {}'.format(port, mac, retry_response))
            return
        else:
            error_message = 'dial failed, error: {}'.format(retry_response)
            print(error_message)
            quit()


def get_ip(ip_dic, db,):
    """
    flag: True表示ip有效，False表示ip已经失效
    :param db_eq:数据库类
    :param log: 日志类
    :return:
    """
    print('Current Thread Name %s, ' % (threading.currentThread().name, ))
    print('need dial MAC is : {}'.format(ip_dic.get('mac')))
    while True:
        # 失效IP重新拨号
        new_ip = redail_ip(ip_dic.get('mac'), ip_dic.get('port'), db)
        if not new_ip:
            break
        # 检查是否在历史IP库中
        old_res = db['bad_ip_results'].find_one({'ip': new_ip})
        if old_res:
            # IP已经重复出现次数+1
            db['bad_ip_results'].update_one({'_id': old_res.get('_id')}, {'$set': {'bad_count': old_res.get('bad_count') + 1}})
            print(' this IP is repeat...time sleep 20s...')
            time.sleep(20)
            quit()
        else:
            print('New IP:{}'.format(new_ip))
            # 新IP添加到历史库，重复出现次数为0
            db['bad_ip_results'].insert_one({'ip': new_ip, 'bad_count': 0})
            #  IP列表更新IP
            db['back_ip_results'].update_one({'mac': ip_dic.get('mac')}, {'$set': {'ip': new_ip, 'flag': True, 'updateTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'port': ip_dic.get('port')}})
            # 补充道IP池
            db['ip_results'].insert_one({'mac': ip_dic.get('mac'), 'ip': new_ip, 'updateTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
            break




if __name__ == '__main__':
    """mongo配置"""
    client = pymongo.MongoClient("mongodb://root:root962540@10.0.0.55:27017")
    db = client['ip_db']
    ip_collection = db['ip_results']
    back_ip_collection = db['back_ip_results']
    # vps_static_ip_collection = db['vps_static_ip_results']
    # bad_ip_collection = db['bad_ip_results']
    """--------"""

    while True:
        # 数据库中IP状态为false重新拨号
        res = back_ip_collection.find({'flag': False})
        if res.count():
            mac_list = []
            for _ in res:
                mac_list.append(_)
            startTime = time.time()
            threads = []
            # 设置线程数
            threadNum = len(mac_list)
            for i in range(0, threadNum):
                t = threading.Thread(target=get_ip, args=(mac_list[i], db,))
                threads.append(t)
            for t in threads:
                t.setDaemon(True)
                t.start()
            for t in threads:
                # 多线程多join的情况下，依次执行各线程的join方法, 这样可以确保主线程最后退出， 且各个线程间没有阻塞
                t.join()
            endTime = time.time()
            print('Done, Time cost: %s ' % (endTime - startTime))
        else:
            print('there is not Mac need to dial\n')
            time.sleep(3)
