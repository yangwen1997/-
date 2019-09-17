#author : yangwenlong 

run.py : 企查猫项目入口函数

common : 公告文件夹
    common  : 公共配置
    
redis_to_company    :   公司名录存入redis
mfcode_to_redis     :   解密mfcode参数存入redis
test.py             :   企查猫爬虫程序测试模块
qcm_run.py          :   企查猫爬虫程序

项目介绍:
    企查猫名录基本信息补充
    公司白名单资源从各类网站抓取下来的数据源只有手机号和公司名，进行通过企查猫进行公司名字查询，如果搜索到公司就保存公司
    列表页url存入redis中，如果搜索不到数据就回写mongodb库中标志为失败，通过async + aiohttp 进行从存入redis中搜索到的公司
    抓取详情页中的基本工商信息存入mongo完成数据补充
    

mongodb中标志字段
    redis : 
        none    :   不存在，没有存入过redis
        1       :   写入到redis企查猫名录库成功状态码
        10      :   补充数据完成并存入新表中状态
        2       :   企查猫中没有搜索到公司