#encoding=utf8
import re
import cpca

def companyORaddr(addr):
    """
    解析地区
    :param addr:
    :return:
    """
    try:
        result = cpca.transform([addr])
        companyProvince = result["省"][0]
        companyCity = result["市"][0]
        area = result["区"][0]
    except:
        companyProvince = ""
        companyCity = ""
        area = ""
    return companyProvince, companyCity, area

class parse_addr(object):
    def __new__(cls, *args):
        """
        继承parse_addr 创建一个单列模式
        :param args:
        :return:
        """
        super(parse_addr,cls).__new__(cls)
        addr = args[0]
        company = args[1]

        if addr:
            companyProvince,companyCity,area = companyORaddr(addr)
        else:
            companyProvince,companyCity,area = companyORaddr(company)

        return companyProvince,companyCity,area

# companyProvince, companyCity, area = parse_addr("成都顶呱呱","")

class SQL_insert(object):
    """
    向mysql中插入数据,更新数据，不需要返回值
    """
    def __new__(cls, *args, **kwargs):
        super(SQL_insert,cls).__new__(cls)
        sql = args[0]
        conn = args[1]
        cursor = args[2]
        log = args[3]

        try:
            # print(sql)
            cursor.execute(sql)
            conn.commit()
            log.info("更新成功，sql语句为--{}".format(sql))
        except Exception as e:
            conn.rollback()
            if "for key 'uiq'" in str(e):
                log.info("数据存在已忽略。。。。。。。。。。。")
            else:
                print(e)

        return sql

class SQL_search(object):
    """
    查询mysq中的数据，需要返回值
    """
    def __new__(cls, *args, **kwargs):
        super(SQL_search,cls).__new__(cls)
        sql = args[0]
        conn = args[1]
        cursor = args[2]
        log = args[3]

        assert cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()

        log.info("查询mysql数据成功")
        return result



class tradeClass(object):
    "行业分类"

    def __init__(self,trade):
        self.trade = trade.replace("(","").replace(")","")
        self.trade_class = ""


        # 农业
        self.Agro = "农业，谷物种植,稻谷种植,小麦种植,玉米种植,其他谷物种植,豆类、油料和薯类种植,豆类种植,油料种植,薯类种植,棉、麻、糖、烟草种植,棉花种植,麻类种植,糖料种植,烟草种植,蔬菜、食用菌及园艺作物种植,蔬菜种植,食用菌种植,花卉种植,其他园艺作物种植,水果种植,仁果类和核果类水果种植,葡萄种植,柑橘类种植,香蕉等亚热带水果种植,其他水果种植,坚果、含油果、香料和饮料作物种植,坚果种植,含油果种植,香料作物种植,茶叶种植,其他饮料作物种植,中药材种植,中草药种植,其他中药材种植,草种植及割草,草种植,天然草原割草,其他农业"

        # 林业
        self.Forestry = "林业，林木育种和育苗,林木育种,林木育苗,造林和更新,森林经营、管护和改培,森林经营和管护,森林改培,木材和竹材采运,木材采运,竹材采运,林产品采集,木竹材林产品采集,非木竹材林产品采集"

        #畜牧业
        self.Graziery = "畜牧业，牲畜饲养,牛的饲养,马的饲养,猪的饲养,羊的饲养,骆驼饲养,其他牲畜饲养,家禽饲养,鸡的饲养,鸭的饲养,鹅的饲养,其他家禽饲养,狩猎和捕捉动物,其他畜牧业,兔的饲养,蜜蜂饲养,其他未列明畜牧业"

        # 渔业
        self.Fishery = "渔业，水产养殖,海水养殖,内陆养殖,水产捕捞,海水捕捞,内陆捕捞"

        #农、林、牧、渔专业及辅助性活动
        self.SupAct = "农、林、牧、渔专业及辅助性活动，农业专业及辅助性活动,种子种苗培育活动,农业机械活动,灌溉活动,农产品初加工活动,农作物病虫害防治活动,其他农业专业及辅助性活动,林业专业及辅助性活动,林业有害生物防治活动,森林防火活动,林产品初级加工活动,其他林业专业及辅助性活动,畜牧专业及辅助性活动,畜牧良种繁殖活动,畜禽粪污处理活动,其他畜牧专业及辅助性活动,渔业专业及辅助性活动,鱼苗及鱼种场活动,其他渔业专业及辅助性活动"

        self.AgroLT = [self.Agro, self.Forestry,self.Graziery, self.Fishery,self.SupAct]

        #煤炭开采和洗选业
        self.CoalMining = "烟煤和无烟煤开采洗选,褐煤开采洗选,其他煤炭采选，煤炭开采和洗选业"

        # 石油和天然气开采业
        self.Petroleum = "石油和天然气开采业，石油开采,陆地石油开采,海洋石油开采,天然气开采,陆地天然气开采,海洋天然气及可燃冰开采"

        # 黑色金属矿采选业
        self.BlackMetal = "黑色金属矿采选业，铁矿采选,锰矿、铬矿采选,其他黑色金属矿采选"

        # 有色金属矿采选业
        self.ISMetal = "有色金属矿采选业，常用有色金属矿采选,铜矿采选,铅锌矿采选,镍钴矿采选,锡矿采选,锑矿采选,铝矿采选,镁矿采选,其他常用有色金属矿采选,贵金属矿采选,金矿采选,银矿采选,其他贵金属矿采选,稀有稀土金属矿采选,钨钼矿采选,稀土金属矿采选,放射性金属矿采选,其他稀有金属矿采选"

        # 非金属矿采选业
        self.NotIsMetal = "非金属矿采选业，土砂石开采,石灰石、石膏开采,建筑装饰用石开采,耐火土石开采,粘土及其他土砂石开采,化学矿开采,采盐,石棉及其他非金属矿采选,石棉、云母矿采选,石墨、滑石采选,宝石、玉石采选,其他未列明非金属矿采选"

        #开采专业及辅助性活动
        self.MetalACT = "开采专业及辅助性活动，煤炭开采和洗选专业及辅助性活动,石油和天然气开采专业及辅助性活动,其他开采专业及辅助性活动，煤矿"

        #其他采矿业
        self.OtherMetal = "其他采矿业"

        self.CoalMiningLT = [self.CoalMining,self.Petroleum,self.BlackMetal,self.ISMetal,self.NotIsMetal,self.MetalACT,self.OtherMetal]

        # 农副食品加工业
        self.SideFood = "农副食品加工业，谷物磨制,稻谷加工,小麦加工,玉米加工,杂粮加工,其他谷物磨制,饲料加工,宠物饲料加工,其他饲料加工,植物油加工,食用植物油加工,非食用植物油加工,制糖业,屠宰及肉类加工,牲畜屠宰,禽类屠宰,肉制品及副产品加工,水产品加工,水产品冷冻加工,鱼糜制品及水产品干腌制加工,鱼油提取及制品制造,其他水产品加工,蔬菜、菌类、水果和坚果加工,蔬菜加工,食用菌加工,水果和坚果加工,其他农副食品加工,淀粉及淀粉制品制造,豆制品制造,蛋品加工,其他未列明农副食品加工"

        # 食品制造业
        self.MakeFood = "食品制造业，焙烤食品制造,糕点、面包制造,饼干及其他焙烤食品制造,糖果、巧克力及蜜饯制造,糖果、巧克力制造,蜜饯制作,方便食品制造,米、面制品制造,速冻食品制造,方便面制造,其他方便食品制造,乳制品制造,液体乳制造,乳粉制造,其他乳制品制造,罐头食品制造,肉、禽类罐头制造,水产品罐头制造,蔬菜、水果罐头制造,其他罐头食品制造,调味品、发酵制品制造,味精制造,酱油、食醋及类似制品制造,其他调味品、发酵制品制造,其他食品制造,营养食品制造,保健食品制造,冷冻饮品及食用冰制造,盐加工 ,食品及饲料添加剂制造,其他未列明食品制造"

        # 酒、饮料和精制茶制造业
        self.Wine = "酒、饮料和精制茶制造业，酒的制造,酒精制造,白酒制造,啤酒制造,黄酒制造,葡萄酒制造,其他酒制造,饮料制造,碳酸饮料制造,瓶(罐)装饮用水制造,果菜汁及果菜汁饮料制造,含乳饮料和植物蛋白饮料制造,固体饮料制造,茶饮料及其他饮料制造,精制茶加工"

        # 烟草制品业
        self.Smoke = "烟草制品业，烟叶复烤,卷烟制造,其他烟草制品制造"

        # 纺织业
        self.Spin = "纺织业，棉纺织及印染精加工,棉纺纱加工,棉织造加工,棉印染精加工,毛纺织及染整精加工,毛条和毛纱线加工,毛织造加工,毛染整精加工,麻纺织及染整精加工,麻纤维纺前加工和纺纱,麻织造加工,麻染整精加工,丝绢纺织及印染精加工,缫丝加工,绢纺和丝织加工,丝印染精加工,化纤织造及印染精加工,化纤织造加工,化纤织物染整精加工,针织或钩针编织物及其制品制造,针织或钩针编织物织造,针织或钩针编织物印染精加工,针织或钩针编织品制造,家用纺织制成品制造,床上用品制造,毛巾类制品制造,窗帘、布艺类产品制造,其他家用纺织制成品制造,产业用纺织制成品制造,非织造布制造,绳、索、缆制造,纺织带和帘子布制造,篷、帆布制造,其他产业用纺织制成品制造"

        # 纺织服装、服饰业
        self.SpinC = "纺织服装、服饰业，机织服装制造,运动机织服装制造,其他机织服装制造,针织或钩针编织服装制造,运动休闲针织服装制造,其他针织或钩针编织服装制造,服饰制造"

        # 皮革、毛皮、羽毛及其制品和制鞋业
        self.Leather = "皮革、毛皮、羽毛及其制品和制鞋业，皮革鞣制加工,皮革制品制造,皮革服装制造,皮箱、包(袋)制造,皮手套及皮装饰制品制造 ,其他皮革制品制造,毛皮鞣制及制品加工,毛皮鞣制加工,毛皮服装加工,其他毛皮制品加工,羽毛(绒)加工及制品制造,羽毛(绒)加工,羽毛(绒)制品加工,制鞋业,纺织面料鞋制造,皮鞋制造,塑料鞋制造,橡胶鞋制造,其他制鞋业,"

        # 木材加工和木、竹、藤、棕、草制品业
        self.Wood = "木材加工和木、竹、藤、棕、草制品业，木材加工,锯材加工,木片加工,单板加工,其他木材加工,人造板制造,胶合板制造,纤维板制造,刨花板制造,其他人造板制造,木质制品制造,建筑用木料及木材组件加工,木门窗制造,木楼梯制造,木地板制造,木制容器制造,软木制品及其他木制品制造,竹、藤、棕、草等制品制造,竹制品制造,藤制品制造,棕制品制造,草及其他制品制造,"

        # 家具制造业
        self.Furn = "家具制造业，木质家具制造,竹、藤家具制造,金属家具制造,塑料家具制造,其他家具制造,"

        # 造纸和纸制品业
        self.PaperProducts = "造纸和纸制品业，纸浆制造,木竹浆制造,非木竹浆制造,造纸,机制纸及纸板制造,手工纸制造,加工纸制造,纸制品制造,纸和纸板容器制造,其他纸制品制造,"

        # 印刷和记录媒介复制业
        self.Printing = "印刷和记录媒介复制业，印刷,书、报刊印刷,本册印制,包装装潢及其他印刷,装订及印刷相关服务,记录媒介复制,"

        # 文教、工美、体育和娱乐用品制造业
        self.TeachingOffice ="文教、工美、体育和娱乐用品制造业，文教办公用品制造,文具制造,笔的制造,教学用模型及教具制造,墨水、墨汁制造,其他文教办公用品制造,乐器制造,中乐器制造,西乐器制造,电子乐器制造,其他乐器及零件制造,工艺美术及礼仪用品制造,雕塑工艺品制造,金属工艺品制造,漆器工艺品制造,花画工艺品制造,天然植物纤维编织工艺品制造,抽纱刺绣工艺品制造,地毯、挂毯制造,珠宝首饰及有关物品制造,其他工艺美术及礼仪用品制造,体育用品制造,球类制造,专项运动器材及配件制造,健身器材制造,运动防护用具制造,其他体育用品制造,玩具制造,电玩具制造,塑胶玩具制造,金属玩具制造,弹射玩具制造,娃娃玩具制造,儿童乘骑玩耍的童车类产品制造,其他玩具制造,游艺器材及娱乐用品制造,露天游乐场所游乐设备制造,游艺用品及室内游艺器材制造,其他娱乐用品制造,"

        # 石油、煤炭及其他燃料加工业
        self.RefinedOil = "石油、煤炭及其他燃料加工业，精炼石油产品制造,原油加工及石油制品制造,其他原油制造,煤炭加工,炼焦,煤制合成气生产,煤制液体燃料生产,煤制品制造,其他煤炭加工,核燃料加工,生物质燃料加工,生物质液体燃料生产,生物质致密成型燃料加工,"

        # 化学原料和化学制品制造业
        self.Chemical = "化学原料和化学制品制造业，基础化学原料制造,无机酸制造,无机碱制造,无机盐制造,有机化学原料制造,其他基础化学原料制造,肥料制造,氮肥制造,磷肥制造,钾肥制造,复混肥料制造,有机肥料及微生物肥料制造,其他肥料制造,农药制造,化学农药制造,生物化学农药及微生物农药制造,涂料、油墨、颜料及类似产品制造,涂料制造,油墨及类似产品制造,工业颜料制造,工艺美术颜料制造,染料制造,密封用填料及类似品制造,合成材料制造,初级形态塑料及合成树脂制造,合成橡胶制造,合成纤维单(聚合)体制造,其他合成材料制造,专用化学产品制造,化学试剂和助剂制造,专项化学用品制造,林产化学产品制造,文化用信息化学品制造,医学生产用信息化学品制造,环境污染处理专用药剂材料制造,动物胶制造,其他专用化学产品制造,炸药、火工及焰火产品制造,炸药及火工产品制造,焰火、鞭炮产品制造 ,日用化学产品制造,肥皂及洗涤剂制造,化妆品制造,口腔清洁用品制造,香料、香精制造,其他日用化学产品制造,"

        # 医药制造业
        self.Chemicals = "医药制造业，化学药品原料药制造,化学药品制剂制造,中药饮片加工,中成药生产,兽用药品制造,生物药品制品制造,生物药品制造,基因工程药物和疫苗制造,卫生材料及医药用品制造,药用辅料及包装材料制造,化学纤维制造业,纤维素纤维原料及纤维制造,化纤浆粕制造,人造纤维(纤维素纤维)制造,合成纤维制造,锦纶纤维制造,涤纶纤维制造,腈纶纤维制造,维纶纤维制造,丙纶纤维制造,氨纶纤维制造,其他合成纤维制造,生物基材料制造,生物基化学纤维制造,生物基、淀粉基新材料制造,"

        # 橡胶和塑料制品业
        self.Rubber = "橡胶和塑料制品业，橡胶制品业,轮胎制造,橡胶板、管、带制造,橡胶零件制造,再生橡胶制造,日用及医用橡胶制品制造,运动场地用塑胶制造,其他橡胶制品制造,塑料制品业,塑料薄膜制造,塑料板、管、型材制造,塑料丝、绳及编织品制造,泡沫塑料制造,塑料人造革、合成革制造,塑料包装箱及容器制造,日用塑料制品制造,人造草坪制造,塑料零件及其他塑料制品制造,"

        # 非金属矿物制品业
        self.OtherMetalProd = "非金属矿物制品业，水泥、石灰和石膏制造,水泥制造,石灰和石膏制造,石膏、水泥制品及类似制品制造,水泥制品制造,砼结构构件制造,石棉水泥制品制造,轻质建筑材料制造,其他水泥类似制品制造,砖瓦、石材等建筑材料制造,粘土砖瓦及建筑砌块制造,建筑用石加工,防水建筑材料制造,隔热和隔音材料制造,其他建筑材料制造,玻璃制造,平板玻璃制造,特种玻璃制造,其他玻璃制造,玻璃制品制造,技术玻璃制品制造,光学玻璃制造,玻璃仪器制造,日用玻璃制品制造,玻璃包装容器制造,玻璃保温容器制造,制镜及类似品加工,其他玻璃制品制造,玻璃纤维和玻璃纤维增强塑料制品制造,玻璃纤维及制品制造,玻璃纤维增强塑料制品制造,陶瓷制品制造,建筑陶瓷制品制造,卫生陶瓷制品制造,特种陶瓷制品制造,日用陶瓷制品制造,陈设艺术陶瓷制造,园艺陶瓷制造,其他陶瓷制品制造,耐火材料制品制造,石棉制品制造,云母制品制造,耐火陶瓷制品及其他耐火材料制造,石墨及其他非金属矿物制品制造,石墨及碳素制品制造,其他非金属矿物制品制造,"

        # 黑色金属冶炼和压延加工业
        self.BlackMetalProd = "黑色金属冶炼和压延加工业，炼铁,炼钢,钢压延加工,铁合金冶炼,"

        # 有色金属冶炼和压延加工业
        self.ISMetalProd = "有色金属冶炼和压延加工业，常用有色金属冶炼,铜冶炼,铅锌冶炼,镍钴冶炼,锡冶炼,锑冶炼,铝冶炼,镁冶炼,硅冶炼,其他常用有色金属冶炼,贵金属冶炼,金冶炼,银冶炼,其他贵金属冶炼,稀有稀土金属冶炼,钨钼冶炼,稀土金属冶炼,其他稀有金属冶炼,有色金属合金制造,有色金属压延加工,铜压延加工,铝压延加工,贵金属压延加工,稀有稀土金属压延加工,其他有色金属压延加工,"

        # 金属制品业
        self.MetalProd = "金属制品业，结构性金属制品制造,金属结构制造,金属门窗制造,金属工具制造,切削工具制造,手工具制造,农用及园林用金属工具制造,刀剪及类似日用金属工具制造,其他金属工具制造,集装箱及金属包装容器制造,集装箱制造,金属压力容器制造,金属包装容器及材料制造,金属丝绳及其制品制造,建筑、安全用金属制品制造,建筑、家具用金属配件制造,建筑装饰及水暖管道零件制造,安全、消防用金属制品制造,其他建筑、安全用金属制品制造,金属表面处理及热处理加工,搪瓷制品制造,生产专用搪瓷制品制造,建筑装饰搪瓷制品制造,搪瓷卫生洁具制造,搪瓷日用品及其他搪瓷制品制造,金属制日用品制造,金属制厨房用器具制造,金属制餐具和器皿制造,金属制卫生器具制造,其他金属制日用品制造,铸造及其他金属制品制造,黑色金属铸造,有色金属铸造,锻件及粉末冶金制品制造,交通及公共管理用金属标牌制造,其他未列明金属制品制造,"

        # 通用设备制造业
        self.FlexibleUnit = "通用设备制造业，锅炉及原动设备制造,锅炉及辅助设备制造,内燃机及配件制造,汽轮机及辅机制造,水轮机及辅机制造,风能原动设备制造,其他原动设备制造,金属加工机械制造,金属切削机床制造,金属成形机床制造,铸造机械制造,金属切割及焊接设备制造,机床功能部件及附件制造,其他金属加工机械制造,物料搬运设备制造,轻小型起重设备制造,生产专用起重机制造,生产专用车辆制造,连续搬运设备制造,电梯、自动扶梯及升降机制造,客运索道制造,机械式停车设备制造,其他物料搬运设备制造,泵、阀门、压缩机及类似机械制造,泵及真空设备制造,气体压缩机械制造,阀门和旋塞制造,液压动力机械及元件制造,液力动力机械及元件制造,气压动力机械及元件制造,轴承、齿轮和传动部件制造,滚动轴承制造,滑动轴承制造,齿轮及齿轮减、变速箱制造,其他传动部件制造,烘炉、风机、包装等设备制造,烘炉、熔炉及电炉制造,风机、风扇制造,气体、液体分离及纯净设备制造,制冷、空调设备制造,风动和电动工具制造,喷枪及类似器具制造 ,包装专用设备制造,文化、办公用机械制造,电影机械制造,幻灯及投影设备制造,照相机及器材制造,复印和胶印设备制造,计算器及货币专用设备制造,其他文化、办公用机械制造,通用零部件制造,金属密封件制造,紧固件制造,弹簧制造,机械零部件加工,其他通用零部件制造,其他通用设备制造业,工业机器人制造,特殊作业机器人制造,增材制造装备制造,其他未列明通用设备制造业,"

        # 专用设备制造业
        self.ZYUnit = "专用设备制造业，采矿、冶金、建筑专用设备制造,矿山机械制造,石油钻采专用设备制造,深海石油钻探设备制造,建筑工程用机械制造,建筑材料生产专用机械制造,冶金专用设备制造,隧道施工专用机械制造,化工、木材、非金属加工专用设备制造,炼油、化工生产专用设备制造,橡胶加工专用设备制造,塑料加工专用设备制造,木竹材加工机械制造,模具制造,其他非金属加工专用设备制造,食品、饮料、烟草及饲料生产专用设备制造,食品、酒、饮料及茶生产专用设备制造,农副食品加工专用设备制造,烟草生产专用设备制造,饲料生产专用设备制造,印刷、制药、日化及日用品生产专用设备制造,制浆和造纸专用设备制造,印刷专用设备制造,日用化工专用设备制造,制药专用设备制造,照明器具生产专用设备制造,玻璃、陶瓷和搪瓷制品生产专用设备制造,其他日用品生产专用设备制造,纺织、服装和皮革加工专用设备制造,纺织专用设备制造,皮革、毛皮及其制品加工专用设备制造,缝制机械制造,洗涤机械制造,电子和电工机械专用设备制造,电工机械专用设备制造,半导体器件专用设备制造,电子元器件与机电组件设备制造,其他电子专用设备制造,农、林、牧、渔专用机械制造,拖拉机制造,机械化农业及园艺机具制造,营林及木竹采伐机械制造,畜牧机械制造,渔业机械制造,农林牧渔机械配件制造,棉花加工机械制造,其他农、林、牧、渔业机械制造,医疗仪器设备及器械制造,医疗诊断、监护及治疗设备制造,口腔科用设备及器具制造,医疗实验室及医用消毒设备和器具制造,医疗、外科及兽医用器械制造,机械治疗及病房护理设备制造,康复辅具制造,眼镜制造,其他医疗设备及器械制造,环保、邮政、社会公共服务及其他专用设备制造,环境保护专用设备制造,地质勘查专用设备制造,邮政专用机械及器材制造,商业、饮食、服务专用设备制造,社会公共安全设备及器材制造,交通安全、管制及类似专用设备制造,水资源专用机械制造,其他专用设备制造,汽车制造业,汽车整车制造,汽柴油车整车制造,新能源车整车制造,汽车用发动机制造,改装汽车制造,低速汽车制造,电车制造,汽车车身、挂车制造,汽车零部件及配件制造,"

        # 铁路、船舶、航空航天和其他运输设备制造业
        self.Rould = "铁路、船舶、航空航天和其他运输设备制造业，铁路运输设备制造,高铁车组制造,铁路机车车辆制造,窄轨机车车辆制造,高铁设备、配件制造,铁路机车车辆配件制造,铁路专用设备及器材、配件制造,其他铁路运输设备制造,城市轨道交通设备制造,船舶及相关装置制造,金属船舶制造,非金属船舶制造,娱乐船和运动船制造,船用配套设备制造,船舶改装,船舶拆除,海洋工程装备制造,航标器材及其他相关装置制造,航空、航天器及设备制造,飞机制造,航天器及运载火箭制造,航天相关设备制造,航空相关设备制造,其他航空航天器制造,摩托车制造,摩托车整车制造,摩托车零部件及配件制造,自行车和残疾人座车制造,自行车制造,残疾人座车制造,助动车制造,非公路休闲车及零配件制造,潜水救捞及其他未列明运输设备制造,潜水装备制造,水下救捞装备制造,其他未列明运输设备制造,"

        # 电气机械和器材制造业
        self.ElectricMotor = "电气机械和器材制造业，电机制造,发电机及发电机组制造,电动机制造,微特电机及组件制造,其他电机制造,输配电及控制设备制造,变压器、整流器和电感器制造,电容器及其配套设备制造,配电开关控制设备制造,电力电子元器件制造,光伏设备及元器件制造,其他输配电及控制设备制造,电线、电缆、光缆及电工器材制造,电线、电缆制造,光纤制造,光缆制造,绝缘制品制造,其他电工器材制造,电池制造,锂离子电池制造,镍氢电池制造,铅蓄电池制造,锌锰电池制造,其他电池制造,家用电力器具制造,家用制冷电器具制造,家用空气调节器制造,家用通风电器具制造,家用厨房电器具制造,家用清洁卫生电器具制造,家用美容、保健护理电器具制造,家用电力器具专用配件制造,其他家用电力器具制造,非电力家用器具制造,燃气及类似能源家用器具制造,太阳能器具制造,其他非电力家用器具制造,照明器具制造,电光源制造,照明灯具制造 ,舞台及场地用灯制造,智能照明器具制造,灯用电器附件及其他照明器具制造,其他电气机械及器材制造,电气信号设备装置制造,其他未列明电气机械及器材制造,"

        # 计算机、通信和其他电子设备制造业
        self.Comp = "计算机、通信和其他电子设备制造业，计算机制造,计算机整机制造,计算机零部件制造,计算机外围设备制造,工业控制计算机及系统制造,信息安全设备制造,其他计算机制造,通信设备制造,通信系统设备制造,通信终端设备制造,广播电视设备制造,广播电视节目制作及发射设备制造,广播电视接收设备制造,广播电视专用配件制造,专业音响设备制造,应用电视设备及其他广播电视设备制造,雷达及配套设备制造,非专业视听设备制造,电视机制造,音响设备制造,影视录放设备制造,智能消费设备制造,可穿戴智能设备制造,智能车载设备制造,智能无人飞行器制造,服务消费机器人制造,其他智能消费设备制造,电子器件制造,电子真空器件制造,半导体分立器件制造,集成电路制造,显示器件制造,半导体照明器件制造,光电子器件制造,其他电子器件制造,电子元件及电子专用材料制造,电阻电容电感元件制造,电子电路制造,敏感元件及传感器制造,电声器件及零件制造,电子专用材料制造,其他电子元件制造,其他电子设备制造,"

        # 仪器仪表制造业
        self. Apparatus = "仪器仪表制造业，通用仪器仪表制造,工业自动控制系统装置制造,电工仪器仪表制造,绘图、计算及测量仪器制造,实验分析仪器制造,试验机制造,供应用仪器仪表制造,其他通用仪器制造,专用仪器仪表制造,环境监测专用仪器仪表制造,运输设备及生产用计数仪表制造,导航、测绘、气象及海洋专用仪器制造,农林牧渔专用仪器仪表制造,地质勘探和地震专用仪器制造,教学专用仪器制造,核子及核辐射测量仪器制造,电子测量仪器制造 ,其他专用仪器制造,钟表与计时仪器制造,光学仪器制造,衡器制造,其他仪器仪表制造业,"

        # 其他制造业
        self.Omake = "其他制造业，日用杂品制造,鬃毛加工、制刷及清扫工具制造,其他日用杂品制造,核辐射加工,其他未列明制造业,"

        # 废弃资源综合利用业
        self.WasteResources = "废弃资源综合利用业，金属废料和碎屑加工处理,非金属废料和碎屑加工处理"

        # 金属制品、机械和设备修理业
        self.MetalWork = "金属制品、机械和设备修理业，金属制品修理,通用设备修理,专用设备修理,铁路、船舶、航空航天等运输设备修理,铁路运输设备修理,船舶修理,航空航天器修理,其他运输设备修理,电气设备修理,仪器仪表修理,其他机械和设备修理业,"

        self.SideFoodLT = [self.SideFood,self.MakeFood,self.Wine,self.Smoke,self.Spin,self.SpinC,self.Leather,
                           self.Wood,self.Furn,self.PaperProducts,self.Printing,self.TeachingOffice,self.RefinedOil,self.Chemical,
                           self.Chemicals,self.Rubber,self.OtherMetalProd,self.BlackMetalProd,self.ISMetalProd,self.MetalProd,self.FlexibleUnit,
                           self.ZYUnit,self.Rould,self.ElectricMotor,self.Comp,self.Apparatus,self.Omake,self.WasteResources,
                           self.MetalWork,]

        # 电力、热力生产和供应业
        self.PowerGeneration  = "电力、热力生产和供应业，电力生产,火力发电,热电联产,水力发电,核力发电,风力发电,太阳能发电,生物质能发电,其他电力生产,电力供应,热力生产和供应,"

        # 燃气生产和供应业
        self.GasProduction = "燃气生产和供应业,天然气生产和供应业,液化石油气生产和供应业,煤气生产和供应业,生物质燃气生产和供应业,"

        # 水的生产和供应业
        self.WarteMake = "水的生产和供应业,自来水生产和供应,污水处理及其再生利用,海水淡化处理,其他水的处理、利用与分配,"

        self.PowerGenerationLT = [self.PowerGeneration,self.GasProduction,self.WarteMake]

        # 房屋建筑业
        self.ResidentialHousing = "房屋建筑业，住宅房屋建筑,体育场馆建筑,其他房屋建筑业,"

        # 土木工程建筑业
        self.CivilWorks = "土木工程建筑业，铁路、道路、隧道和桥梁工程建筑,铁路工程建筑,公路工程建筑,市政道路工程建筑 ,城市轨道交通工程建筑,其他道路、隧道和桥梁工程建筑 ,水利和水运工程建筑,水源及供水设施工程建筑,河湖治理及防洪设施工程建筑,港口及航运设施工程建筑,海洋工程建筑,海洋油气资源开发利用工程建筑,海洋能源开发利用工程建筑,海底隧道工程建筑,海底设施铺设工程建筑,其他海洋工程建筑,工矿工程建筑,架线和管道工程建筑,架线及设备工程建筑,管道工程建筑,地下综合管廊工程建筑,节能环保工程施工,节能工程施工,环保工程施工,生态保护工程施工,电力工程施工,火力发电工程施工,水力发电工程施工,核电工程施工,风能发电工程施工,太阳能发电工程施工,其他电力工程施工,其他土木工程建筑,园林绿化工程施工,体育场地设施工程施工,游乐设施工程施工,其他土木工程建筑施工,"

        # 建筑安装业
        self.Construction = "建筑安装业，电气安装,管道和设备安装,其他建筑安装业,体育场地设施安装,其他建筑安装,"

        # 建筑装饰、装修和其他建筑业
        self.ArchitecturalOrnament  = "建筑装饰、装修和其他建筑业，建筑装饰和装修业,公共建筑装饰和装修,住宅装饰和装修,建筑幕墙装饰和装修,建筑物拆除和场地准备活动,建筑物拆除活动,场地准备活动,提供施工设备服务,其他未列明建筑业,"

        self.ArchitecturalOrnamentLT = [self.ResidentialHousing,self.CivilWorks,self.Construction,self.ArchitecturalOrnament]

        # 批发业
        self.WholesaleTrade = "批发业，农、林、牧、渔产品批发,谷物、豆及薯类批发,种子批发,畜牧渔业饲料批发,棉、麻批发,林业产品批发,牲畜批发,渔业产品批发,其他农牧产品批发,食品、饮料及烟草制品批发,米、面制品及食用油批发,糕点、糖果及糖批发,果品、蔬菜批发,肉、禽、蛋、奶及水产品批发,盐及调味品批发,营养和保健品批发,酒、饮料及茶叶批发,烟草制品批发,其他食品批发,纺织、服装及家庭用品批发,纺织品、针织品及原料批发,服装批发,鞋帽批发,化妆品及卫生用品批发,厨具卫具及日用杂品批发,灯具、装饰物品批发,家用视听设备批发,日用家电批发,其他家庭用品批发,文化、体育用品及器材批发,文具用品批发,体育用品及器材批发,图书批发,报刊批发,音像制品、电子和数字出版物批发,首饰、工艺品及收藏品批发,乐器批发,其他文化用品批发,医药及医疗器材批发,西药批发,中药批发,动物用药品批发,医疗用品及器材批发,矿产品、建材及化工产品批发,煤炭及制品批发,石油及制品批发,非金属矿及制品批发,金属及金属矿批发,建材批发,化肥批发,农药批发,农用薄膜批发,其他化工产品批发,机械设备、五金产品及电子产品批发,农业机械批发,汽车及零配件批发,摩托车及零配件批发,五金产品批发,电气设备批发,计算机、软件及辅助设备批发,通讯设备批发,广播影视设备批发,其他机械设备及电子产品批发,贸易经纪与代理,贸易代理,一般物品拍卖 ,艺术品、收藏品拍卖,艺术品代理,其他贸易经纪与代理,其他批发业,再生物资回收与批发,宠物食品用品批发,互联网批发,其他未列明批发业,"

        # 零售业
        self.RetailIndustry = "零售业，综合零售,百货零售,超级市场零售,便利店零售,其他综合零售,食品、饮料及烟草制品专门零售,粮油零售,糕点、面包零售,果品、蔬菜零售,肉、禽、蛋、奶及水产品零售,营养和保健品零售,酒、饮料及茶叶零售,烟草制品零售,其他食品零售,纺织、服装及日用品专门零售,纺织品及针织品零售,服装零售,鞋帽零售,化妆品及卫生用品零售,厨具卫具及日用杂品零售,钟表、眼镜零售,箱包零售,自行车等代步设备零售,其他日用品零售,文化、体育用品及器材专门零售,文具用品零售,体育用品及器材零售,图书、报刊零售,音像制品、电子和数字出版物零售,珠宝首饰零售,工艺美术品及收藏品零售,乐器零售,照相器材零售,其他文化用品零售,医药及医疗器材专门零售,西药零售,中药零售,动物用药品零售,医疗用品及器材零售,保健辅助治疗器材零售,汽车、摩托车、零配件和燃料及其他动力销售,汽车新车零售,汽车旧车零售,汽车零配件零售,摩托车及零配件零售,机动车燃油零售,机动车燃气零售,机动车充电销售,家用电器及电子产品专门零售 ,家用视听设备零售,日用家电零售,计算机、软件及辅助设备零售,通信设备零售,其他电子产品零售,五金、家具及室内装饰材料专门零售,五金零售,灯具零售,家具零售,涂料零售,卫生洁具零售,木质装饰材料零售,陶瓷、石材装饰材料零售,其他室内装饰材料零售,货摊、无店铺及其他零售业,流动货摊零售,互联网零售,邮购及电视、电话零售,自动售货机零售,旧货零售,生活用燃料零售,宠物食品用品零售,其他未列明零售业,"

        self.RetailIndustryLT = [self.WholesaleTrade,self.RetailIndustry]
        # 铁路运输业
        self.RailwayTransportation = "铁路运输业，铁路旅客运输,高速铁路旅客运输,城际铁路旅客运输,普通铁路旅客运输,铁路货物运输,铁路运输辅助活动,客运火车站,货运火车站(场),铁路运输维护活动,其他铁路运输辅助活动,"

        # 道路运输业
        self.RoadTransport  = "道路运输业，城市公共交通运输,公共电汽车客运,城市轨道交通,出租车客运,公共自行车服务,其他城市公共交通运输 ,公路旅客运输,长途客运,旅游客运,其他公路客运,道路货物运输,普通货物道路运输,冷藏车道路运输,集装箱道路运输,大型货物道路运输,危险货物道路运输,邮件包裹道路运输,城市配送,搬家运输,其他道路货物运输,道路运输辅助活动,客运汽车站,货运枢纽(站),公路管理与养护,其他道路运输辅助活动,"

        # 水上运输业
        self.WaterTransport = "水上运输业，水上旅客运输,海上旅客运输,内河旅客运输,客运轮渡运输,水上货物运输,远洋货物运输,沿海货物运输,内河货物运输,水上运输辅助活动,客运港口,货运港口,其他水上运输辅助活动,"

        # 航空运输业
        self.AirTransportIndustry = "航空运输业，航空客货运输,航空旅客运输,航空货物运输,通用航空服务,通用航空生产服务,观光游览航空服务,体育航空运动服务,其他通用航空服务,航空运输辅助活动,机场,空中交通管理,其他航空运输辅助活动,"

        # 管道运输业
        self.PipelineTransportation = "管道运输业，海底管道运输,陆地管道运输"

        # 多式联运和运输代理业
        self.MultimodalTransport  = "多式联运和运输代理业，多式联运,运输代理业,货物运输代理,旅客票务代理,其他运输代理业,"

        # 装卸搬运和仓储业
        self.TransportationHandling = "装卸搬运和仓储业，装卸搬运,通用仓储,低温仓储,危险品仓储,油气仓储,危险化学品仓储,其他危险品仓储,谷物、棉花等农产品仓储,谷物仓储,棉花仓储,其他农产品仓储,中药材仓储,其他仓储业,"

        # 邮政业
        self.MailBusiness = "邮政业，邮政基本服务,快递服务,其他寄递服务,"

        self.MailBusinessLT = [self.RailwayTransportation,self.RoadTransport,self.WaterTransport,self.AirTransportIndustry,
                               self.PipelineTransportation,self.MultimodalTransport,self.TransportationHandling]

        # 住宿业
        self.HotelIndustry  ="住宿业，旅游饭店,一般旅馆,经济型连锁酒店,其他一般旅馆,民宿服务,露营地服务,其他住宿业,"

        # 餐饮业
        self.CateringServices = "餐饮业,正餐服务,快餐服务,饮料及冷饮服务,茶馆服务,咖啡馆服务,酒吧服务 ,其他饮料及冷饮服务,餐饮配送及外卖送餐服务,餐饮配送服务,外卖送餐服务,其他餐饮业,小吃服务,其他未列明餐饮业,"

        self.CateringServicesLT = [self.HotelIndustry,self.CateringServices]

        # 电信、广播电视和卫星传输服务
        self.RadioAndTelevision = "电信、广播电视和卫星传输服务，电信,固定电信服务,移动电信服务,其他电信服务,广播电视传输服务,有线广播电视传输服务,无线广播电视传输服务,卫星传输服务,广播电视卫星传输服务,其他卫星传输服务,"

        # 互联网和相关服务
        self.InternetAndRelated = "互联网和相关服务，互联网接入及相关服务,互联网信息服务 ,互联网搜索服务,互联网游戏服务,互联网其他信息服务,互联网平台,互联网生产服务平台,互联网生活服务平台,互联网科技创新平台,互联网公共服务平台,其他互联网平台,互联网安全服务,互联网数据服务,其他互联网服务"

        # 软件和信息技术服务业
        self.SoftwareAndInformation = "软件和信息技术服务业，软件开发,基础软件开发,支撑软件开发,应用软件开发,其他软件开发,集成电路设计,信息系统集成和物联网技术服务,信息系统集成服务,物联网技术服务,运行维护服务,信息处理和存储支持服务,信息技术咨询服务,数字内容服务,地理遥感信息服务,动漫、游戏数字内容服务,其他数字内容服务,其他信息技术服务业,呼叫中心,其他未列明信息技术服务业,"

        self.SoftwareAndInformationLT = [self.RadioAndTelevision,self.InternetAndRelated,self.SoftwareAndInformation]

        # 货币金融服务
        self.MonetaryAndFinancial = "货币金融服务，中央银行服务,货币银行服务,商业银行服务,政策性银行服务,信用合作社服务,农村资金互助社服务,其他货币银行服务,非货币银行服务,融资租赁服务,财务公司服务 ,典当,汽车金融公司服务,小额贷款公司服务 ,消费金融公司服务 ,网络借贷服务,其他非货币银行服务,银行理财服务,银行监管服务,"

        # 资本市场服务
        self.CapitalMarketServices = "资本市场服务，证券市场服务,证券市场管理服务,证券经纪交易服务,公开募集证券投资基金,非公开募集证券投资基金,创业投资基金,天使投资,其他非公开募集证券投资基金,期货市场服务,期货市场管理服务,其他期货市场服务,证券期货监管服务,资本投资服务,其他资本市场服务,"

        # 保险业
        self.InsuranceIndustry = "保险业，人身保险,人寿保险,年金保险,健康保险,意外伤害保险,财产保险,再保险,商业养老金,保险中介服务,保险经纪服务,保险代理服务,保险公估服务,保险资产管理,保险监管服务,其他保险活动,"

        # 其他金融业
        self.OtherFinancialSectors = "其他金融业，金融信托与管理服务,信托公司,其他金融信托与管理服务,控股公司服务,非金融机构支付服务,金融信息服务,金融资产管理公司,其他未列明金融业,货币经纪公司服务,其他未包括金融业,"

        self.OtherFinancialSectorsLT = [self.MonetaryAndFinancial,self.CapitalMarketServices,self.InsuranceIndustry,self.OtherFinancialSectors]


        # 房地产业
        self.RealEstate  = "房地产业，房地产开发经营,物业管理,房地产中介服务,房地产租赁经营,其他房地产业,"

        self.RealEstateLT = [self.RealEstate]
        # 租赁业
        self.LeasingIndustry  = "租赁业，机械设备经营租赁,汽车租赁,农业机械经营租赁,建筑工程机械与设备经营租赁,计算机及通讯设备经营租赁,医疗设备经营租赁,其他机械与设备经营租赁,文体设备和用品出租,休闲娱乐用品设备出租,体育用品设备出租,文化用品设备出租,图书出租,音像制品出租,其他文体设备和用品出租,日用品出租,"

        # 商务服务业
        self.CommercialServiceIndustry = "商务服务业,组织管理服务,企业总部管理,投资与资产管理,资源与产权交易服务,单位后勤管理服务,农村集体经济组织管理,其他组织管理服务,综合管理服务,园区管理服务,商业综合体管理服务,市场管理服务,供应链管理服务,其他综合管理服务,法律服务,律师及相关法律服务,公证服务,其他法律服务,咨询与调查,会计、审计及税务服务,市场调查,社会经济咨询,健康咨询,环保咨询,体育咨询,其他专业咨询与调查,广告业,互联网广告服务,其他广告服务,人力资源服务,公共就业服务,职业中介服务,劳务派遣服务,创业指导服务,其他人力资源服务,安全保护服务,安全服务,安全系统监控服务,其他安全保护服务,会议、展览及相关服务,科技会展服务,旅游会展服务,体育会展服务,文化会展服务,其他会议、展览及相关服务,其他商务服务业,旅行社及相关服务,包装服务,办公服务,翻译服务,信用服务,非融资担保服务,商务代理代办服务,票务代理服务,其他未列明商务服务业,"

        self.LeasingIndustryLT = [self.LeasingIndustry,self.CommercialServiceIndustry]

        # 研究和试验发展
        self.ResearchAndExperimental = "研究和试验发展,自然科学研究和试验发展,工程和技术研究和试验发展,农业科学研究和试验发展,医学研究和试验发展,社会人文科学研究,"

        # 专业技术服务业
        self.ProfessionalTechnicalService = "专业技术服务业,气象服务,地震服务,海洋服务,海洋气象服务,海洋环境服务,其他海洋服务,测绘地理信息服务,遥感测绘服务,其他测绘地理信息服务,质检技术服务,检验检疫服务,检测服务,计量服务,标准化服务,认证认可服务,其他质检技术服务,环境与生态监测检测服务,环境保护监测,生态资源监测,野生动物疫源疫病防控监测,地质勘查 ,能源矿产地质勘查,固体矿产地质勘查,水、二氧化碳等矿产地质勘查,基础地质勘查,地质勘查技术服务,工程技术与设计服务,工程管理服务,工程监理服务,工程勘察活动,工程设计活动,规划设计管理,土地规划服务,工业与专业设计及其他专业技术服务,工业设计服务,专业设计服务,兽医服务,其他未列明专业技术服务业,"

        # 科技推广和应用服务业
        self.TechnologyPromotion  = "科技推广和应用服务业,技术推广服务,农林牧渔技术推广服务,生物技术推广服务,新材料技术推广服务,节能技术推广服务,新能源技术推广服务,环保技术推广服务,三维(3D)打印技术推广服务,其他技术推广服务,知识产权服务,科技中介服务,创业空间服务,其他科技推广服务业"

        self.TechnologyPromotionLT = [self.ResearchAndExperimental,self.ProfessionalTechnicalService,self.TechnologyPromotion]


        # 水利管理业
        self.WaterManagement = "水利管理业,防洪除涝设施管理,水资源管理,天然水收集与分配,水文服务,其他水利管理业,生态保护和环境治理业,生态保护,自然生态系统保护管理,自然遗迹保护管理,野生动物保护,野生植物保护,动物园、水族馆管理服务,植物园管理服务,其他自然保护,环境治理业,水污染治理,大气污染治理,固体废物治理,危险废物治理,放射性废物治理,土壤污染治理与修复服务,噪声与振动控制服务,其他污染治理 ,"

        # 公共设施管理业
        self.PublicFacilitiesManagement = "公共设施管理业,市政设施管理,环境卫生管理,城乡市容管理 ,绿化管理,城市公园管理,游览景区管理,名胜风景区管理,森林公园管理,其他游览景区管理,"

        # 生态保护和环境治理业
        self.EcologicalProtection = "生态保护和环境治理业,生态保护,自然生态系统保护管理,自然遗迹保护管理,野生动物保护,野生植物保护,动物园、水族馆管理服务,植物园管理服务,其他自然保护,环境治理业,水污染治理,大气污染治理,固体废物治理,危险废物治理,放射性废物治理,土壤污染治理与修复服务,噪声与振动控制服务,其他污染治理 ,"
        # 土地管理业
        self.LandManagement = "土地管理业,土地整治服务,土地调查评估服务,土地登记服务,土地登记代理服务,其他土地管理服务,"

        self.LandManagementLT = [self.WaterManagement,self.PublicFacilitiesManagement,self.EcologicalProtection,self.LandManagement]

        # 居民服务业
        self.ResidentialServices = "居民服务业,家庭服务,托儿所服务,洗染服务,理发及美容服务,洗浴和保健养生服务,洗浴服务,足浴服务,养生保健服务,摄影扩印服务,婚姻服务,殡葬服务,其他居民服务业,"

        # 机动车、电子产品和日用产品修理业
        self.MotorVehicles = "机动车、电子产品和日用产品修理业,汽车、摩托车等修理与维护,汽车修理与维护,大型车辆装备修理与维护,摩托车修理与维护,助动车等修理与维护,计算机和办公设备维修,计算机和辅助设备修理,通讯设备修理,其他办公设备维修,家用电器修理,家用电子产品修理,日用电器修理 ,其他日用产品修理业,自行车修理,鞋和皮革修理,家具和相关物品修理,其他未列明日用产品修理业,"

        # 其他服务业
        self.OtherServices = "其他服务业,清洁服务,建筑物清洁服务,其他清洁服务,宠物服务,宠物饲养,宠物医院服务,宠物美容服务,宠物寄托收养服务,其他宠物服务,其他未列明服务业,"

        self.OtherServicesLT = [self.ResidentialServices,self.MotorVehicles,self.OtherServices]

        # 教育
        self.education = "教育,学前教育,初等教育,普通小学教育,成人小学教育,中等教育,普通初中教育,职业初中教育,成人初中教育,普通高中教育,成人高中教育,中等职业学校教育,高等教育,普通高等教育,成人高等教育,特殊教育,技能培训、教育辅助及其他教育,职业技能培训,体校及体育培训,文化艺术培训,教育辅助服务,其他未列明教育,"

        self.educationLT = [self.education]
        # 卫生
        self.sanitation = "卫生,医院,综合医院,中医医院,中西医结合医院,民族医院,专科医院,疗养院,基层医疗卫生服务,社区卫生服务中心(站),街道卫生院,乡镇卫生院,村卫生室,门诊部(所),专业公共卫生服务,疾病预防控制中心,专科疾病防治院所、站,妇幼保健院(所、站),急救中心(站)服务,采供血机构服务,计划生育技术服务活动,其他卫生活动,健康体检服务,临床检验服务,其他未列明卫生服务,"

        # 社会工作
        self.WorkInAdditon = "社会工作,提供住宿社会工作,干部休养所,护理机构服务,精神康复服务,老年人、残疾人养护服务,临终关怀服务,孤残儿童收养和庇护服务,其他提供住宿社会救助,不提供住宿社会工作,社会看护与帮助服务,康复辅具适配服务,其他不提供住宿社会工作,"

        self.WorkInAdditonLT = [self.sanitation,self.WorkInAdditon]

        # 新闻和出版业
        self.NewsAndPublishing = "新闻和出版业,新闻业,出版业,图书出版,报纸出版,期刊出版,音像制品出版,电子出版物出版,数字出版,其他出版业,"

        # 广播、电视、电影和录音制作业
        self.FilmAndRrecording = "广播、电视、电影和录音制作业,广播,电视,影视节目制作,广播电视集成播控,电影和广播电视节目发行,电影放映,录音制作,"

        # 文化艺术业
        self.ArtsAndCulture = "文化艺术业,文艺创作与表演,艺术表演场馆,图书馆与档案馆,图书馆,档案馆,文物及非物质文化遗产保护,博物馆,烈士陵园、纪念馆,群众文体活动,其他文化艺术业,"

        # 体育
        self.sports  = "体育,体育组织,体育竞赛组织,体育保障组织,其他体育组织,体育场地设施管理,体育场馆管理,其他体育场地设施管理 ,健身休闲活动,其他体育,体育中介代理服务,体育健康服务,其他未列明体育,"

        # 娱乐业
        self.ShowBusiness =  "娱乐业,室内娱乐活动,歌舞厅娱乐活动,电子游艺厅娱乐活动,网吧活动,其他室内娱乐活动,游乐园,休闲观光活动,彩票活动,体育彩票服务,福利彩票服务,其他彩票服务,文化体育娱乐活动与经纪代理服务,文化活动服务,体育表演服务,文化娱乐经纪人,体育经纪人,其他文化艺术经纪代理,其他娱乐业,"

        self.ShowBusinessLT = [self.NewsAndPublishing,self.FilmAndRrecording,self.ArtsAndCulture,self.sports,self.ShowBusiness]

        # 中国共产党机关
        self.OrgansOfCommunist= "中国共产党机关,中国共产党机关"

        # 国家机构
        self.StateInstitution = "国家机构,国家权力机构,国家行政机构,综合事务管理机构,对外事务管理机构,公共安全管理机构,社会事务管理机构,经济事务管理机构,行政监督检查机构,监察委员会、人民法院和人民检察院,监察委员会,人民法院,人民检察院,其他国家机构,消防管理机构,其他未列明国家机构,"

        # 人民政协、民主党派
        self.PeoplesGovernment = "人民政协、民主党派,人民政协,民主党派"

        # 社会保障
        self.SocialIinsurance= "社会保障,基本保险,基本养老保险,基本医疗保险,失业保险,工伤保险,生育保险,其他基本保险,补充保险,其他社会保障,"

        # 群众团体、社会团体和其他成员组织
        self.MassOrganization= "群众团体、社会团体和其他成员组织,群众团体,工会,妇联,共青团,其他群众团体,社会团体,专业性团体,行业性团体,其他社会团体,基金会,宗教组织,宗教团体服务,宗教活动场所服务,"

        # 基层群众自治组织
        self.GrassRoots= "基层群众自治组织,社区居民自治组织,村民自治组织"

        self.GrassRootsLT = [self.OrgansOfCommunist,self.StateInstitution,self.PeoplesGovernment,self.SocialIinsurance,self.MassOrganization,self.GrassRoots]

        # 国际组织
        self.InternationalOrganization = "国际组织"
        self.InternationalOrganizationLT = [self.InternationalOrganization]

    def run(self):

        try:
            for _ in self.AgroLT:
                if re.search(self.trade, _.replace(" ","").replace("(","").replace(")",""),):
                    self.trade_class = "农林牧渔业"
                    return self.trade_class
            for _ in self.CoalMiningLT:
                if re.search(self.trade, _.replace(" ","").replace("(","").replace(")",""),):
                    self.trade_class = "采矿业"
                    return self.trade_class
            notSideFoodLT = ["卫生"]
            for _ in self.SideFoodLT:
                if self.trade not in notSideFoodLT:
                    if re.search(self.trade, _.replace(" ","").replace("(","").replace(")",""),):
                        self.trade_class = "制造业"
                        return self.trade_class
            for _ in self.PowerGenerationLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "电气热水业"
                    return self.trade_class
            for _ in self.ArchitecturalOrnamentLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "建筑业"
                    return self.trade_class
            notRetailIndustryLT = ["卫生","数字出版"]
            if self.trade not in notRetailIndustryLT:
                for _ in self.RetailIndustryLT:
                    if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                        self.trade_class = "批发零售业"
                        return self.trade_class
            for _ in self.MailBusinessLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "交通运输与存储邮政业"
                    return self.trade_class
            for _ in self.CateringServicesLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "餐饮业"
                    return self.trade_class
            for _ in self.SoftwareAndInformationLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "软件和信息技术服务业"
                    return self.trade_class
            for _ in self.OtherFinancialSectorsLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "金融业"
                    return self.trade_class
            for _ in self.RealEstateLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "房地产业"
                    return self.trade_class
            for _ in self.LeasingIndustryLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "租赁和商务服务业"
                    return self.trade_class
            for _ in self.TechnologyPromotionLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "科学研究和技术服务业"
                    return self.trade_class
            notLandManagementLT = ["卫生"]
            # notLandManagementLT = []
            for _ in self.LandManagementLT:
                if self.trade not in notLandManagementLT:
                    if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                        self.trade_class = "水利、环境和公共设施管理业"
                        return self.trade_class
            notOtherServicesLT = ["医院"]
            for _ in self.OtherServicesLT:
                if self.trade not in notOtherServicesLT:
                    if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                        self.trade_class = "居民服务、修理和其他服务业"
                        return self.trade_class
            for _ in self.educationLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "教育"
                    return self.trade_class
            for _ in self.WorkInAdditonLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "卫生和社会工作"
                    return self.trade_class
            for _ in self.ShowBusinessLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "文化、体育和娱乐业"
                    return self.trade_class
            for _ in self.GrassRootsLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "公共管理、社会保障和社会组织"
                    return self.trade_class
            for _ in self.InternationalOrganizationLT:
                if re.search(self.trade, _.replace(" ", "").replace(")","").replace("(","")):
                    self.trade_class = "国际组织"
                    return self.trade_class

            return "其他类别"

        except Exception as e:
            print(e)