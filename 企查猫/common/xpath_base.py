


class XPATH(object):
    def __init__(self):
        # 邮箱  统一社会信用代码 注册号 机构代码 法定代表人 企业类型 经营状态 注册资本
        self.companyEmail = '//div[@class="arthd_info"]/*[contains(text(),"企业地址")]/text()'
        self.creditCode = '//*[contains(text(),"统一社会信用代码：")]/following-sibling::span/text()'
        self.registerNum = '//*[contains(text(),"注册号：")]/following-sibling::span/text()'
        self.OrganizationCode = '//*[contains(text(),"机构代码：")]/following-sibling::span/text()'
        self.legalMan = '//*[contains(text(),"法定代表人：")]/following-sibling::span//text()'
        self.companyType = '//*[contains(text(),"企业类型：")]/following-sibling::span//text()'
        self.businessState = '//*[contains(text(),"经营状态：")]/following-sibling::span//text()'
        self.registerMoney = '//*[contains(text(),"注册资本：")]/following-sibling::span//text()'

        # 成立日期  登记机关 经营期限 所属地区 核准日期 经营范围
        self.registerTime = '//*[contains(text(),"成立日期：")]/following-sibling::span//text()'
        self.registOrgan = '//*[contains(text(),"登记机关：")]/following-sibling::span//text()'
        self.operating_period = '//*[contains(text(),"经营期限：")]/following-sibling::span//text()'
        self.area = '//*[contains(text(),"所属地区：")]/following-sibling::span//text()'
        self.approval_time = '//*[contains(text(),"核准日期：")]/following-sibling::span//text()'
        self.scope = '//*[contains(text(),"经营范围：")]/following-sibling::span//text()'

        #变更总数  最近的变更项目 变更前 变更后
        self.changeInfoCount = '//*[contains(text(),"经营范围：")]/following-sibling::span//text()'
        self.changeInfo_project = '//ul[@class="art-change list-bgxx"]/li[1]//*[contains(text(),"变更项目")]/following-sibling::text()'
        self.changeInfo_after = '//ul[@class="art-change list-bgxx"]/li[1]//*[contains(text(),"变更前")]/following-sibling::text()'
        self.changeInfo_end = '//ul[@class="art-change list-bgxx"]/li[1]//*[contains(text(),"变更后")]/following-sibling::text()'
        self.changeInfo_time = '//ul[@class="art-change list-bgxx"]/li[1]//*[contains(text(),"变更后")]/ancestor::div/following-sibling::p/time/text()'

