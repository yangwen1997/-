from storage_mysql import Storage
from easydict import EasyDict
from sq_144.common import m_db,get_log
log = get_log()

# mongo_data = m_db.find_one({"_id":"c8e17a5c4f9f91cce3307642554c95b5"})
mongo_datas = m_db.find({})

try:
    for mongo_data in mongo_datas:
        base_item = EasyDict()
        base_item.companyName = mongo_data["companyName"]
        base_item._id = mongo_data["_id"]
        base_item.collectTime = mongo_data["collectTime"]
        base_item.companyUrl = mongo_data["companyUrl"]
        base_item.webSource = mongo_data["webSource"]

        base_item.baseInfo = mongo_data["base"]["baseInfo"]
        base_item.changeInfoCount = mongo_data["base"]["changeInfoCount"]
        base_item.productInfoCount = mongo_data["base"]["productInfoCount"]
        base_item.courtNoticeInfoCount = mongo_data["lawDangerous"]["courtNoticeInfoCount"]
        base_item.noticesInfoCount = mongo_data["lawDangerous"]["noticesInfoCount"]
        base_item.trademarkInfoCount = mongo_data["knowledgeProperty"]["trademarkInfoCount"]
        base_item.patentInfoCount = mongo_data["knowledgeProperty"]["patentInfoCount"]
        base_item.copyrightInfoCount = mongo_data["knowledgeProperty"]["copyrightInfoCount"]
        base_item.copyrightSoftInfoCount = mongo_data["knowledgeProperty"]["copyrightSoftInfoCount"]
        base_item.certificateInfoCount = mongo_data["knowledgeProperty"]["certificateInfoCount"]

        #基本信息
        Storage().gsjbxx(base_item)

        #股东信息
        if mongo_data["base"]["holderInfo"]:
            item_lt = mongo_data["base"]["holderInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().gdxx(item)

        #主要人员
        if mongo_data["base"]["employeeInfo"]:
            item_lt = mongo_data["base"]["employeeInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().employeeInfo(item)

        #工商变更
        if mongo_data["base"]["changeInfo"]:
            item_lt = mongo_data["base"]["changeInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().changeInfo(item)

        #分支机构
        if mongo_data["base"]["branchInfo"]:
            item_lt = mongo_data["base"]["branchInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().branchInfo(item)

        #产品信息
        if mongo_data["base"]["productInfo"]:
            item_lt = mongo_data["base"]["productInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().productInfo(item)

        #裁判文书
        if mongo_data["lawDangerous"]["lawSuitsInfo"]:
            item_lt = mongo_data["lawDangerous"]["lawSuitsInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().lawSuitsInfo(item)

        #被执行人
        if mongo_data["lawDangerous"]["executedPersonInfo"]:
            item_lt = mongo_data["lawDangerous"]["executedPersonInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().executedPersonInfo(item)

        #开庭公告
        if mongo_data["lawDangerous"]["courtNoticeInfo"]:
            item_lt = mongo_data["lawDangerous"]["courtNoticeInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().courtNoticeInfo(item)

        #法院公告
        if mongo_data["lawDangerous"]["noticesInfo"]:
            item_lt = mongo_data["lawDangerous"]["noticesInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().noticesInfo(item)

        #失信信息
        if mongo_data["lawDangerous"]["executionInfo"]:
            item_lt = mongo_data["lawDangerous"]["executionInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().executionInfo(item)

        #经营异常
        if mongo_data["lawDangerous"]["abnormalInfo"]:
            item_lt = mongo_data["lawDangerous"]["abnormalInfo"]
            for item in item_lt:
                item = item[0]
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().abnormalInfo(item)

        #股权冻结
        if mongo_data["lawDangerous"]["equityFreezeInfo"]:
            item_lt = mongo_data["lawDangerous"]["equityFreezeInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().equityFreezeInfo(item)

        #立案信息
        if mongo_data["lawDangerous"]["caseInfo"]:
            item_lt = mongo_data["lawDangerous"]["caseInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().caseInfo(item)

        #土地抵押
        if mongo_data["lawDangerous"]["tddyInfo"]:
            item_lt = mongo_data["lawDangerous"]["tddyInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().tddyInfo(item)

        #商标信息
        if mongo_data["knowledgeProperty"]["trademarkInfo"]:
            item_lt = mongo_data["knowledgeProperty"]["trademarkInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().trademarkInfo(item)

        # 专利信息
        if mongo_data["knowledgeProperty"]["patentInfo"]:
            item_lt = mongo_data["knowledgeProperty"]["patentInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().patentInfo(item)

        # 作品著作权
        if mongo_data["knowledgeProperty"]["copyrightInfo"]:
            item_lt = mongo_data["knowledgeProperty"]["copyrightInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().copyrightInfo(item)

        # 软件著作权
        if mongo_data["knowledgeProperty"]["copyrightSoftInfo"]:
            item_lt = mongo_data["knowledgeProperty"]["copyrightSoftInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().copyrightSoftInfo(item)

        # 资质认证
        if mongo_data["knowledgeProperty"]["certificateInfo"]:
            item_lt = mongo_data["knowledgeProperty"]["certificateInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().certificateInfo(item)

        # 对外投资
        if mongo_data["correlation"]["investmentInfo"]:
            item_lt = mongo_data["correlation"]["investmentInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().investmentInfo(item)

        # 融资信息
        if mongo_data["development"]["financeDataInfo"]:
            item_lt = mongo_data["development"]["financeDataInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().financeDataInfo(item)

        # 质权人
        if mongo_data["development"]["pawneeInfo"]:
            item_lt = mongo_data["development"]["pawneeInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().pawneeInfo(item)

        # 行政许可
        if mongo_data["development"]["admLicenseInfo"]:
            item_lt = mongo_data["development"]["admLicenseInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().admLicenseInfo(item)

        # 招投标
        if mongo_data["development"]["biddingInfo"]:
            item_lt = mongo_data["development"]["biddingInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().biddingInfo(item)

        # 地块公示
        if mongo_data["development"]["tdgsInfo"]:
            item_lt = mongo_data["development"]["tdgsInfo"]
            for item in item_lt:
                item["companyName"] = base_item.companyName
                item["_id"] = base_item._id
                Storage().tdgsInfo(item)

        log.info("数据{}分表存入mysql完成".format(mongo_data["_id"]))
except Exception as e:
    print(e)
