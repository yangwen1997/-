import pymysql
from sq_144.common import cursor,get_log,conn

log = get_log()
class Storage(object):
    """
    存储到mysql中的方法
    """
    def __init__(self):
        pass

    @staticmethod
    def run_sql(sql):
        """
        运行sql
        :return:
        """
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            #运行出错，回滚事件
            if "for key 'uiq'" in str(e):
                pass
            else:
                conn.rollback()
                print(e)

    @staticmethod
    def ISNONE(item,key):
        """
        判断值是否是NONE值
        :param item:
        :param key:
        :return:
        """
        try:
            result = item[key]
        except:
            result = None
        return result
    @classmethod
    def gsjbxx(cls,item):
        """
        工商基本信息
        :param args:
        :return:
        """
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["legal_person"] = item["baseInfo"]["legalMan"]
            items["register_capital"] = item["baseInfo"]["registerMoney"]
            items["manage_state"] = item["baseInfo"]["businessState"]

            items["contributed_capital"] = None
            items["create_date"] = item["baseInfo"]["registerTime"]
            items["credit_code"] = item["baseInfo"]["creditCode"]
            items["ratepaying_num"] = None
            items["register_num"] = item["baseInfo"]["registerNum"]
            items["organization_code"] = item["baseInfo"]["OrganizationCode"]
            items["enterprise_type"] = item["baseInfo"]["companyType"]

            items["trade"] = None
            items["check_date"] = None
            items["register_addr"] = item["baseInfo"]["registOrgan"]
            items["english_name"] = None
            items["used_name"] = None
            items["insurance_person_nums"] = None
            items["person_scale"] = None
            items["business_deadline"] = item["baseInfo"]["businessTimeout"]

            items["enterprise_addr"] = item["baseInfo"]["registerAddress"]
            items["manage_scope"] = item["baseInfo"]["businessScope"]
            items["collectTime"] = item["collectTime"]
            items["companyUrl"] = item["companyUrl"]
            items["webSource"] = item["webSource"]
            items["holderInfoCount"] = None
            items["employeeInfoCount"] = None
            items["changeInfoCount"] = item["changeInfoCount"]

            items["productInfoCount"] = item["productInfoCount"]
            items["lawSuitsInfoCount"] = None
            items["executedPersonInfoCount"] = None
            items["courtNoticeInfoCount"] = item["courtNoticeInfoCount"]
            items["noticesInfoCount"] = item["noticesInfoCount"]
            items["executionInfoCount"] = None

            items["abnormalInfoCount"] = None
            items["equityFreezeInfoCount"] = None
            items["caseInfoCount"] = None
            items["tddyInfoCount"] = None
            items["trademarkInfoCount"] = item["trademarkInfoCount"]
            items["patentInfoCount"] = item["patentInfoCount"]
            items["copyrightInfoCount"] = item["copyrightInfoCount"]

            items["copyrightSoftInfoCount"] = item["copyrightSoftInfoCount"]
            items["certificateInfoCount"] = item["certificateInfoCount"]
            items["investmentInfoCount"] = None
            items["financeDataInfoCount"] = None
            items["pawneeInfoCount"] = None
            items["admLicenseInfoCount"] = None
            items["biddingInfoCount"] = None
            items["tdgsInfoCount"] = None

            sql = "insert into gsjbxx(company_name,_id,page_company_name,legal_person,register_capital,manage_state,contributed_capital,create_date,credit_code,ratepaying_num,register_num,organization_code,enterprise_type,trade,check_date,register_addr,english_name,used_name,insurance_person_nums,person_scale,business_deadline,enterprise_addr,manage_scope,collectTime,companyUrl,webSource,holderInfoCount,employeeInfoCount,changeInfoCount,productInfoCount,lawSuitsInfoCount,executedPersonInfoCount,courtNoticeInfoCount,noticesInfoCount,executionInfoCount,abnormalInfoCount,equityFreezeInfoCount,caseInfoCount,tddyInfoCount,trademarkInfoCount,patentInfoCount,copyrightInfoCount,copyrightSoftInfoCount,certificateInfoCount,investmentInfoCount,financeDataInfoCount,pawneeInfoCount,admLicenseInfoCount,biddingInfoCount,tdgsInfoCount) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')" .format(items["company_name"], items["_id"], items["page_company_name"], items["legal_person"], items["register_capital"], items["manage_state"], items["contributed_capital"], items["create_date"], items["credit_code"], items["ratepaying_num"], items["register_num"], items["organization_code"], items["enterprise_type"], items["trade"], items["check_date"],items["register_addr"], items["english_name"], items["used_name"], items["insurance_person_nums"], items["person_scale"], items["business_deadline"], items["enterprise_addr"],items["manage_scope"],items["collectTime"],items["companyUrl"],items["webSource"],items["holderInfoCount"],items["employeeInfoCount"],items["changeInfoCount"], items["productInfoCount"], items["lawSuitsInfoCount"], items["executedPersonInfoCount"], items["courtNoticeInfoCount"], items["noticesInfoCount"], items["executionInfoCount"], items["abnormalInfoCount"] , items["equityFreezeInfoCount"] , items["caseInfoCount"] , items["tddyInfoCount"] , items["trademarkInfoCount"] , items["patentInfoCount"] , items["copyrightInfoCount"] , items["copyrightSoftInfoCount"] , items["certificateInfoCount"] , items["investmentInfoCount"] , items["financeDataInfoCount"] , items["pawneeInfoCount"], items["admLicenseInfoCount"], items["biddingInfoCount"], items["tdgsInfoCount"])
            Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def gdxx(cls,item):
        "股东信息"
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["shareholder"] = Storage().ISNONE(item,"hiName")
            items["share_holding"] = None
            items["contributive"] = Storage().ISNONE(item,"hiContribu")

            sql = "insert into gdxx(company_name, _id, page_company_name, shareholder, share_holding, contributive) values('{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["shareholder"], items["share_holding"], items["contributive"])
            Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def employeeInfo(cls,item):
        """主要人员"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["scPosition"] = Storage().ISNONE(item, "scPosition")
            items["scName"] = Storage().ISNONE(item, "scName")

            if items["scName"]:
                sql = "insert into employeeInfo(company_name, _id, page_company_name, scPosition, scName) values('{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"], items["scPosition"], items["scName"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)


    @classmethod
    def changeInfo(cls,item):
        """工商变更"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["change_date"] = Storage().ISNONE(item, "changeTime")
            items["change_matter"] = Storage().ISNONE(item, "changeItem")
            items["change_Before"] = Storage().ISNONE(item, "changeBefore")
            items["change_end"] = Storage().ISNONE(item,"changeAfter")
            if items["change_matter"]:
                sql = "insert into gsbg(company_name, _id, page_company_name, change_date, change_matter, change_Before, change_end) values('{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["change_date"], items["change_matter"], items["change_Before"], items["change_end"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def branchInfo(cls,item):
        """分支机构"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["bCompanyName"] = Storage().ISNONE(item, "bCompanyName")
            items["bName"] = Storage().ISNONE(item, "bName")
            if items["bName"]:
                sql = "insert into branchInfo(company_name, _id, page_company_name, bCompanyName, bName) values('{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["bCompanyName"], items["bName"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def productInfo(cls,item):
        """产品信息"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["product_name"] = Storage().ISNONE(item, "pAllName")
            items["product_intro"] = Storage().ISNONE(item, "pDescribe")
            items["product_class"] = Storage().ISNONE(item, "pClassify")
            items["territory"] = Storage().ISNONE(item, "pField")
            if items["product_name"]:
                sql = "insert into cpxx(company_name, _id, page_company_name, product_name, product_intro, product_class, territory) values('{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["product_name"], items["product_intro"], items["product_class"], items["territory"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def lawSuitsInfo(cls,item):
        """裁判文书"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["cpwsJudgeTime"] = Storage().ISNONE(item,"cpwsJudgeTime")
            items["cpwsIdentity"] = Storage().ISNONE(item,"cpwsIdentity")
            items["cpwsName"] = Storage().ISNONE(item,"cpwsName")
            items["cpwsResult"] = Storage().ISNONE(item,"cpwsResult")
            if items["cpwsName"]:
                sql = "insert into lawSuitsInfo(company_name, _id, page_company_name, cpwsJudgeTime, cpwsIdentity, cpwsName, cpwsResult) values('{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["cpwsJudgeTime"], items["cpwsIdentity"], items["cpwsName"], items["cpwsResult"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def executedPersonInfo(cls,item):
        """被执行人"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["zCaseTime"] = Storage().ISNONE(item, "zCaseTime")
            items["zCaseNum"] = Storage().ISNONE(item, "zCaseNum")
            items["zTarget"] = Storage().ISNONE(item, "zTarget")
            items["zCourt"] = Storage().ISNONE(item, "zCourt")
            if items["zCaseNum"]:
                sql = "insert into executedPersonInfo(company_name, _id, page_company_name, zCaseTime, zCaseNum, zTarget, zCourt) values('{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["zCaseTime"], items["zCaseNum"],items["zTarget"], items["zCourt"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def courtNoticeInfo(cls,item):
        """开庭公告"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["aLawfulDay"] = Storage().ISNONE(item, "aLawfulDay")
            items["aCaseNum"] = Storage().ISNONE(item, "aCaseNum")
            items["aCaseReason"] = Storage().ISNONE(item, "aCaseReason")
            items["aJudge"] = Storage().ISNONE(item, "aJudge")
            items["aAppellor"] = Storage().ISNONE(item, "aAppellor")
            items["aDefendant"] = Storage().ISNONE(item, "aDefendant")
            if items["aCaseNum"]:
                sql = "insert into courtNoticeInfo(company_name, _id, page_company_name, aLawfulDay, aCaseNum, aCaseReason, aJudge,aAppellor,aDefendant) values('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["aLawfulDay"], items["aCaseNum"],items["aCaseReason"], items["aJudge"], items["aAppellor"], items["aDefendant"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def noticesInfo(cls,item):
        """法院公告"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]
            items["cDate"] = Storage().ISNONE(item, "cDate")
            items["cType"] = Storage().ISNONE(item, "cType")
            items["aDefendant"] = Storage().ISNONE(item, "aDefendant")
            items["cJudge"] = Storage().ISNONE(item, "cJudge")
            items["cInfo"] = Storage().ISNONE(item, "cInfo")

            if items["aDefendant"]:
                sql = "insert into noticesInfo(company_name, _id, page_company_name, cDate, cType, aDefendant, cJudge,cInfo) values('{}','{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["cDate"], items["cType"],items["aDefendant"], items["cJudge"], items["cInfo"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def executionInfo(cls,item):
        """失信信息"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["diName"] = Storage().ISNONE(item, "diName")
            items["diIdentify"] = Storage().ISNONE(item, "diIdentify")
            items["diLowMan"] = Storage().ISNONE(item, "diLowMan")
            items["diPublishTime"] = Storage().ISNONE(item, "diPublishTime")
            items["diCourt"] = Storage().ISNONE(item, "diCourt")

            items["dProvince"] = Storage().ISNONE(item, "dProvince")
            items["diDepend"] = Storage().ISNONE(item, "diDepend")
            items["dFilingDate"] = Storage().ISNONE(item, "dFilingDate")
            items["diNum"] = Storage().ISNONE(item, "diNum")
            items["diUnit"] = Storage().ISNONE(item, "diUnit")

            items["diPerform"] = Storage().ISNONE(item, "diPerform")
            items["diDuty"] = Storage().ISNONE(item, "diDuty")
            items["diStatus"] = Storage().ISNONE(item, "diStatus")

            if items["diNum"]:
                sql = "insert into executionInfo(company_name, _id, page_company_name,  diName, diIdentify, diLowMan, diPublishTime,diCourt, dProvince, diDepend, dFilingDate, diNum,diUnit, diPerform, diDuty ,diStatus) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["diName"], items["diIdentify"],items["diLowMan"], items["diPublishTime"], items["diCourt"],items["dProvince"], items["diDepend"],items["dFilingDate"], items["diNum"], items["diUnit"],items["diPerform"], items["diDuty"],items["diStatus"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def abnormalInfo(cls,item):
        """经营异常"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["ruInTime"] = Storage().ISNONE(item, "ruInTime")
            items["ruSection"] = Storage().ISNONE(item, "ruSection")
            items["ruInCause"] = Storage().ISNONE(item, "ruInCause")
            items["ruOutTime"] = Storage().ISNONE(item, "ruOutTime")
            items["ruOutCause"] = Storage().ISNONE(item, "ruOutCause")

            if items["ruSection"]:
                sql = "insert into abnormalInfo(company_name, _id, page_company_name, ruInTime, ruSection, ruInCause, ruOutTime,ruOutCause) values('{}','{}','{}','{}','{}','{}','{}','{}')".format(items["company_name"], items["_id"], items["page_company_name"], items["ruInTime"], items["ruSection"],items["ruInCause"], items["ruOutTime"], items["ruOutCause"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def equityFreezeInfo(cls,item):
        """股权冻结"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["ruInTime"] = None
            items["frzCourt"] = Storage().ISNONE(item, "frzCourt")
            items["frzThings"] = Storage().ISNONE(item, "frzThings")
            items["frzExeNum"] = Storage().ISNONE(item, "frzExeNum")
            items["frzNotNum"] = Storage().ISNONE(item, "frzNotNum")

            items["frzPHNum"] = Storage().ISNONE(item, "frzPHNum")
            items["frzType"] = Storage().ISNONE(item, "frzType")
            items["frzCode"] = Storage().ISNONE(item, "frzCode")
            items["frzFrom"] = Storage().ISNONE(item, "frzFrom")
            items["frzTo"] = Storage().ISNONE(item, "frzTo")

            items["frzLine"] = Storage().ISNONE(item, "frzLine")
            items["frzShowDate"] = Storage().ISNONE(item, "frzShowDate")
            items["frzOutTime"] = Storage().ISNONE(item, "frzOutTime")
            items["frzOutReason"] = Storage().ISNONE(item, "frzOutReason")

            if items["frzExeNum"]:
                sql = "insert into equityFreezeInfo(company_name, _id, page_company_name,  ruInTime, frzCourt, frzThings, frzExeNum,frzNotNum, frzPHNum, frzType, frzCode, frzFrom,frzTo, frzLine, frzShowDate ,frzOutTime,frzOutReason) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"], items["ruInTime"], items["frzCourt"],
                    items["frzThings"], items["frzExeNum"], items["frzNotNum"], items["frzPHNum"], items["frzType"],
                    items["frzCode"], items["frzFrom"], items["frzTo"], items["frzLine"], items["frzShowDate"],
                    items["frzOutTime"], items["frzOutReason"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def caseInfo(cls,item):
        """立案信息"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["caseNum"] = Storage().ISNONE(item, "caseNum")
            items["caseJudge"] = Storage().ISNONE(item, "caseJudge")
            items["caseHelper"] = Storage().ISNONE(item, "caseHelper")
            items["caseTime"] = Storage().ISNONE(item, "caseTime")
            items["caseOpen"] = Storage().ISNONE(item, "caseOpen")

            items["endTime"] = Storage().ISNONE(item, "endTime")
            items["caseStatus"] = Storage().ISNONE(item, "caseStatus")
            items["plaintiff"] = Storage().ISNONE(item, "plaintiff")

            if items["plaintiff"]:
                items["plaintiff"] = items["plaintiff"].replace("\xa0","")

            items["defendant"] = Storage().ISNONE(item, "defendant")

            if items["caseNum"]:
                sql = "insert into caseInfo(company_name, _id, page_company_name, caseNum, caseJudge, caseHelper, caseTime,caseOpen, endTime, caseStatus, plaintiff, defendant) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"], items["caseNum"], items["caseJudge"],
                    items["caseHelper"], items["caseTime"], items["caseOpen"], items["endTime"], items["caseStatus"],
                    items["plaintiff"], items["defendant"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def tddyInfo(cls,item):
        """土地抵押"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["lmNum"] =  Storage().ISNONE(item, "lmNum")
            items["lmArea"] =  Storage().ISNONE(item, "lmArea")
            items["lmOcreage"] =  Storage().ISNONE(item, "lmOcreage")
            items["lmAcreage"] =  Storage().ISNONE(item, "lmAcreage")
            items["lmMoney"] = Storage().ISNONE( item, "lmMoney")

            items["lmBeMoney"] =  Storage().ISNONE(item, "lmBeMoney")
            items["lmLocation"] =  Storage().ISNONE(item, "lmLocation")
            items["lmUse"] =  Storage().ISNONE(item, "lmUse")
            items["lmOtherCode"] =  Storage().ISNONE(item, "lmOtherCode")
            items["lmUseCode"] =  Storage().ISNONE(item, "lmUseCode")

            items["lmManName"] =  Storage().ISNONE(item, "lmManName")
            items["lmManIdenty"] =  Storage().ISNONE(item, "lmManIdenty")
            items["lmMan"] =  Storage().ISNONE(item, "lmMan")
            items["lmType"] =  Storage().ISNONE(item, "lmType")
            items["lmFrom"] =  Storage().ISNONE(item, "lmFrom")

            items["lmTo"] =  Storage().ISNONE(item, "lmTo")

            if items["lmManName"]:
                sql = "insert into tddyInfo(company_name, _id, page_company_name, lmNum, lmArea, lmOcreage, lmAcreage,lmMoney,  lmBeMoney, lmLocation, lmUse, lmOtherCode, lmUseCode, lmManName, lmManIdenty, lmMan, lmType, lmFrom, lmTo) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["lmNum"], items["lmArea"], items["lmOcreage"], items["lmAcreage"], items["lmMoney"],
                    items["lmBeMoney"], items["lmLocation"], items["lmUse"], items["lmOtherCode"], items["lmUseCode"],
                    items["lmManName"], items["lmManIdenty"], items["lmMan"], items["lmType"], items["lmFrom"],
                    items["lmTo"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def trademarkInfo(cls,item):
        """商标信息"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["application_date"] = item["tmApplyTime"]

            items["brand"] = Storage().ISNONE(item, "tmName")
            if items["brand"]:
                items["brand"] = items["brand"] .replace("'","")

            items["brand_name"] =  Storage().ISNONE(item, "tmName")
            if items["brand_name"]:
                items["brand_name"] = items["brand_name"] .replace("'","")

            items["register_num"] =  Storage().ISNONE(item, "tmRegisterNum")
            items["international_class"] =  Storage().ISNONE(item, "tmClassify")

            items["brand_state"] =  Storage().ISNONE(item, "tmStatus")
            items["info_url"] =  Storage().ISNONE(item, "info_url")

            if items["brand_name"]:
                sql = "insert into sbxx(company_name, _id, page_company_name, application_date, brand, brand_name, register_num,international_class,  brand_state, info_url) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["application_date"], items["brand"], items["brand_name"], items["register_num"], items["international_class"],
                    items["brand_state"], items["info_url"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def patentInfo(cls,item):
        """ 专利信息"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["apply_date"] =  Storage().ISNONE(item, "piApplyAnnounceDate")
            items["patent_name"] =  Storage().ISNONE(item, "piInventName")
            items["patent_type"] =  Storage().ISNONE(item, "piClassifyNum")


            # if items["patent_name"]:
            sql = "insert into sbxx(company_name, _id, page_company_name, application_date, brand, brand_name) values('{}','{}','{}','{}','{}','{}')".format(
                items["company_name"], items["_id"], items["page_company_name"],
                pymysql.escape_string(str(items["apply_date"])), pymysql.escape_string(str(items["patent_name"])), items["patent_type"])
            Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def copyrightInfo(cls,item):
        """作品著作权"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["works_name"] =  Storage().ISNONE(item, "pwName")
            if items["works_name"]:
                items["works_name"] = items["works_name"].replace("'","")
            items["works_class"] =  Storage().ISNONE(item, "pwCategory")
            items["target_date"] =  Storage().ISNONE(item, "pwFinishDate")
            items["register_date"] =  Storage().ISNONE(item, "pwRegisterDate")
            items["first_relaise_date"] =  Storage().ISNONE(item, "pwPublishDate")

            if items["works_name"]:
                sql = "insert into zpzzq(company_name, _id, page_company_name, works_name, works_class, target_date, register_date, first_relaise_date) values('{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["works_name"], items["works_class"], items["target_date"], items["register_date"], items["first_relaise_date"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def copyrightSoftInfo(cls,item):
        """软件著作权"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["ratify_date"] = Storage().ISNONE(item, "swRegisterDate")
            items["software_full_name"] = Storage().ISNONE(item, "swAllName")
            if items["software_full_name"]:
                items["software_full_name"] = items["software_full_name"].replace("'","")
            items["software_intro"] = Storage().ISNONE(item, "swName")
            items["class_num"] = Storage().ISNONE(item, "swClassifyNum")

            if items["software_full_name"]:
                sql = "insert into rjzzq(company_name, _id, page_company_name, ratify_date, software_full_name, software_intro, class_num) values('{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["ratify_date"], items["software_full_name"], items["software_intro"], items["class_num"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def certificateInfo(cls,item):
        """资质认证"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["certiDate"] =  Storage().ISNONE(item, "certiDate")
            items["certiType"] =  Storage().ISNONE(item, "certiType")
            items["certiEndTime"] =  Storage().ISNONE(item, "certiEndTime")
            items["certiNum"] =  Storage().ISNONE(item, "certiNum")
            items["ceriStatus"] =  Storage().ISNONE(item, "ceriStatus")

            items["certiMore"] =  Storage().ISNONE(item, "certiMore")

            if items["certiNum"]:
                sql = "insert into certificateInfo(company_name, _id, page_company_name, certiDate, certiType, certiEndTime, certiNum, ceriStatus, certiMore) values('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["certiDate"], items["certiType"], items["certiEndTime"], items["certiNum"],
                    items["ceriStatus"], pymysql.escape_string(items["certiMore"]))
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def investmentInfo(cls,item):
        """对外投资"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["iiCompany"] =  Storage().ISNONE(item, "iiCompany")
            items["iiName"] =  Storage().ISNONE(item, "iiName")
            items["iiCapital"] =  Storage().ISNONE(item, "iiCapital")
            items["iiBuild"] =  Storage().ISNONE(item, "iiBuild")


            if items["iiCompany"]:
                sql = "insert into investmentInfo(company_name, _id, page_company_name, iiCompany, iiName, iiCapital, iiBuild) values('{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["iiCompany"], items["iiName"], items["iiCapital"], items["iiBuild"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def financeDataInfo(cls,item):
        """融资信息"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["financing_info"] =  Storage().ISNONE(item, "financing_info")
            items["financing_num"] =  Storage().ISNONE(item, "financing_num")
            items["financing_money"] =  Storage().ISNONE(item, "financing_money")
            items["investor"] =  Storage().ISNONE(item, "investor")

            if items["financing_info"]:
                sql = "insert into rzxx(company_name, _id, page_company_name, financing_info, financing_num, financing_money, investor) values('{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["financing_info"], items["financing_num"], items["financing_money"], items["investor"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def pawneeInfo(cls,item):
        """质权人"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["eyRegisterNum"] =  Storage().ISNONE(item, "eyRegisterNum")
            items["eyStatus"] =  Storage().ISNONE(item, "eyStatus")
            items["eyoName"] =  Storage().ISNONE(item, "eyoName")
            items["eyoMoneyNum"] =  Storage().ISNONE(item, "eyoMoneyNum")
            items["eyoMan"] =  Storage().ISNONE(item, "eyoMan")

            items["eyMan"] =  Storage().ISNONE(item, "eyMan")
            items["eyNum"] =  Storage().ISNONE(item, "eyNum")
            items["eyTime"] =  Storage().ISNONE(item, "eyTime")
            items["eMore"] =  Storage().ISNONE(item, "eMore")

            if items["eyRegisterNum"]:
                sql = "insert into pawneeInfo(company_name, _id, page_company_name, eyRegisterNum, eyStatus, eyoName, eyoMoneyNum,eyoMan, eyMan, eyNum, eyTime, eMore) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["eyRegisterNum"], items["eyStatus"], items["eyoName"], items["eyoMoneyNum"], items["eyoMan"],
                    items["eyMan"], items["eyNum"], items["eyTime"], items["eMore"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def admLicenseInfo(cls,item):
        """行政许可"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["license_file_num"] =  Storage().ISNONE(item, "gsLicenceNum")
            items["license_file"] =  Storage().ISNONE(item, "gsLicenceName")
            items["start_deadline"] =  Storage().ISNONE(item, "gsDeadlineStart")
            items["end_deadline"] =  Storage().ISNONE(item, "gsDeadlineEnd")
            items["license_office"] =  Storage().ISNONE(item, "gsOrgan")

            if items["license_file_num"]:
                sql = "insert into xzxk(company_name, _id, page_company_name, license_file_num, license_file, start_deadline, end_deadline,license_office) values('{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["license_file_num"], items["license_file"], items["start_deadline"], items["end_deadline"], items["license_office"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def biddingInfo(cls,item):
        """招投标"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["bPublishTime"] =  Storage().ISNONE(item, "bPublishTime")
            items["bTitle"] =  Storage().ISNONE(item, "bTitle")
            items["bMan"] =  Storage().ISNONE(item, "bMan")
            items["bArea"] =  Storage().ISNONE(item, "bArea")
            items["bClassify"] =  Storage().ISNONE(item, "bClassify")

            if items["bTitle"]:
                sql = "insert into biddingInfo(company_name, _id, page_company_name, bPublishTime, bTitle, bMan, bArea,bClassify) values('{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["bPublishTime"], items["bTitle"], items["bMan"], items["bArea"], items["bClassify"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)

    @classmethod
    def tdgsInfo(cls,item):
        """地块公示"""
        try:
            items = {}
            items["company_name"] = item["companyName"]
            items["_id"] = item["_id"]
            items["page_company_name"] = item["companyName"]

            items["lpNum"] =  Storage().ISNONE(item, "lpNum")
            items["lpDate"] =  Storage().ISNONE(item, "lpDate")
            items["lparea"] =  Storage().ISNONE(item, "lparea")
            items["lpAdmin"] =  Storage().ISNONE(item, "lpAdmin")
            items["lpLocation"] =  Storage().ISNONE(item, "lpLocation")

            items["lpName"] =  Storage().ISNONE(item, "lpName")
            items["lpBelong"] =  Storage().ISNONE(item, "lpBelong")
            items["lpUse"] =  Storage().ISNONE(item, "lpUse")
            items["lpFrom"] =  Storage().ISNONE(item, "lpFrom")
            items["lpTo"] =  Storage().ISNONE(item, "lpTo")

            if items["lpNum"]:
                sql = "insert into tdgsInfo(company_name, _id, page_company_name,  lpNum, lpDate, lparea, lpAdmin,lpLocation, lpName, lpBelong, lpUse, lpFrom,lpTo) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    items["company_name"], items["_id"], items["page_company_name"],
                    items["lpNum"], items["lpDate"], items["lparea"], items["lpAdmin"], items["lpLocation"],
                    items["lpName"], items["lpBelong"], items["lpUse"], items["lpFrom"], items["lpTo"])
                Storage().run_sql(sql)
        except Exception as e:
            print(e)



