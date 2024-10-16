from sqlalchemy import create_engine, Column, INT, VARCHAR, Sequence, FLOAT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 子弹信息类
class Ammo:
    """
    存储子弹信息的类
    """
    id: int  # id
    name: str  # 名称
    caliber: str  # 口径
    weight: float  # 重量
    stackMaxSize: int  # 堆叠数量
    tracer: bool  # 是否有弹迹
    tracerColor: str  # 弹迹颜色
    damage: str  # 肉伤
    armorDamage: float  # 护甲伤害
    fragmentationChance: float  # 碎弹几率
    ricochetChance: float  # 跳弹几率
    penetrationPower: int  # 穿甲力
    accuracyModifier: float  # 精度修正
    recoilModifier: float  # 后坐力修正
    lightBleedModifier: float  # 小出血修正
    heavyBleedModifier: float  # 大出血修正
    img: str  # 图片名
    marketSale: int  # 是否禁售
    apiID: str  # API ID
    projectileCount: int  # 弹丸数量
    initialSpeed: float  # 初速
    staminaBurnPerDamage: float  # 消耗体力


    # 构造函数
    def __init__(self,
                 id: int,
                 name: str,
                 caliber: str,
                 weight: float,
                 stackMaxSize: int,
                 tracer: bool,
                 tracerColor: str,
                 damage: str,
                 armorDamage: float,
                 fragmentationChance: float,
                 ricochetChance: float,
                 penetrationPower: int,
                 accuracyModifier: float,
                 recoilModifier: float,
                 lightBleedModifier: float,
                 heavyBleedModifier: float,
                 img: str,
                 marketSale: int,
                 apiID: str,
                 projectileCount: int,
                 initialSpeed: float,
                 staminaBurnPerDamage: float):
        """
        构造函数
        :param id: int [id]
        :param name: str [名称]
        :param caliber: str [口径]
        :param weight: float [重量]
        :param stackMaxSize: int [堆叠数量]
        :param tracer: bool [是否有弹迹]
        :param tracerColor: str [弹迹颜色]
        :param damage: str [肉伤]
        :param armorDamage: float [护甲伤害]
        :param fragmentationChance: float [碎弹几率]
        :param ricochetChance: float [跳弹几率]
        :param penetrationPower: int [穿甲力]
        :param accuracyModifier: float [精度修正]
        :param recoilModifier: float [后坐力修正]
        :param lightBleedModifier: float [小出血修正]
        :param heavyBleedModifier: float [大出血修正]
        :param img: str [图片名]
        :param marketSale: int [是否禁售]
        :param apiID: str [API ID]
        :param projectileCount: int [弹丸数量]
        :param initialSpeed: float [初速]
        :param staminaBurnPerDamage: float [消耗体力]
        """
        self.id = id
        self.name = name
        self.caliber = caliber
        self.weight = weight
        self.stackMaxSize = stackMaxSize
        self.tracer = True if int(tracer) == 1 else False
        self.tracerColor = tracerColor
        self.damage = damage
        self.armorDamage = armorDamage
        self.fragmentationChance = fragmentationChance
        self.ricochetChance = ricochetChance
        self.penetrationPower = penetrationPower
        self.accuracyModifier = accuracyModifier
        self.recoilModifier = recoilModifier
        self.lightBleedModifier = lightBleedModifier
        self.heavyBleedModifier = heavyBleedModifier
        self.img = img
        self.marketSale = marketSale
        self.apiID = apiID
        self.projectileCount = projectileCount
        self.initialSpeed = initialSpeed
        self.staminaBurnPerDamage = staminaBurnPerDamage


# 购买来源
class ItemPrice:
    """
    存储购买/售出信息的类
    """
    price: int  # 价格
    currency: str  # 货币
    priceRUB: int  # 价格（卢布）
    source: str  # 来源
    requirements: list[dict]  # 需求材料 dict

    # 构造函数
    def __init__(self, price: int, currency: str, priceRUB: int, source: str, requirements: list[dict]):
        """
        构造函数
        :param price: int [价格]
        :param currency: str [货币]
        :param priceRUB: int [价格（卢布）]
        :param source: str [来源]
        :param requirements: list[dict] [需求材料]
        """
        self.price = price
        self.currency = currency
        self.priceRUB = priceRUB
        self.source = source
        self.requirements = requirements


# 合成来源
class Craft:
    """
    存储合成信息的类
    """
    name: str  # 名称
    level: int  # 等级
    duration: int  # 时间
    requirements: list[dict]  # 材料 dict(name, count)

    # 构造函数
    def __init__(self, name: str, level: int, duration: int, requirements: list[dict]):
        """
        构造函数
        :param name: str [名称]
        :param level: int [等级]
        :param duration: int [时间]
        :param requirements: list[dict] [材料 dict(name, count)]
        """
        self.name = name
        self.level = level
        self.duration = duration
        self.requirements = requirements


# 子弹详细信息类
class AmmoMoreInfo:
    """
    存储子弹额外信息的类
    """
    basePrice: int  # 基础价格
    avg24hPrice: int  # 24小时平均价格
    fleaMarketPrice: int  # 跳蚤市场最近价格
    buyFor: list[ItemPrice]  # 购买来源
    craftsFor: list[Craft]  # 合成来源

    # 构造函数
    def __init__(self,
                 basePrice: int,
                 avg24hPrice: int,
                 buyFor: list[ItemPrice],
                 craftsFor: list[Craft],
                 fleaMarketPrice: int
        ):
        """
        构造函数
        :param basePrice: int [基础价格]
        :param avg24hPrice: int [24小时平均价格]
        :param buyFor: list[ItemPrice] [购买来源]
        :param craftsFor: list[Craft] [合成来源]
        :param fleaMarketPrice: int [跳蚤市场最近价格]
        """
        self.basePrice = basePrice
        self.avg24hPrice = avg24hPrice
        self.buyFor = buyFor
        self.craftsFor = craftsFor
        self.fleaMarketPrice = fleaMarketPrice


# 物品信息类
class ItemInfo:
    """
    name: str 名称
    shortName: str 短名称
    hasGrid: bool 是否有格子
    basePrice: int 基础价格
    width: int 宽度
    height: int 高度
    img: str 图片名
    category: str 类别
    avg24hPrice: int 24小时平均价格
    low24hPrice: int 24小时最低价格
    high24hPrice: int 24小时最高价格
    accuracyModifier: float 精度修正
    recoilModifier: float 后坐力修正
    ergonomicsModifier: float 人体工学修正
    weight: float 重量
    sellFor: ItemPrice 出售来源
    buyFor: list[ItemPrice] 购买来源
    craftsFor: list[Craft] 合成来源
    craftsUsing: list[Craft] 使用来源
    """
    name: str  # 名称
    shortName: str  # 短名称
    hasGrid: bool  # 是否有格子
    basePrice: int  # 基础价格
    width: int  # 宽度
    height: int  # 高度
    img: str  # 图片名
    category: str  # 类别
    avg24hPrice: int  # 24小时平均价格
    low24hPrice: int  # 24小时最低价格
    high24hPrice: int  # 24小时最高价格
    accuracyModifier: float  # 精度修正
    recoilModifier: float  # 后坐力修正
    ergonomicsModifier: float  # 人体工学修正
    weight: float  # 重量
    sellFor: ItemPrice  # 出售来源
    buyFor: list[ItemPrice]  # 购买来源
    craftsFor: list[Craft]  # 合成来源
    craftsUsing: list[Craft]  # 使用来源
    fleaMarketPrice: int  # 跳蚤市场最近价格

    def __init__(
            self,
            name: str,
            shortName: str,
            hasGrid: bool,
            basePrice: int,
            width: int,
            height: int,
            img: str,
            category: str,
            avg24hPrice: int,
            low24hPrice: int,
            high24hPrice: int,
            accuracyModifier: float,
            recoilModifier: float,
            ergonomicsModifier: float,
            weight: float,
            sellFor: ItemPrice,
            buyFor: list[ItemPrice],
            craftsFor: list[Craft],
            craftsUsing: list[Craft],
            fleaMarketPrice: int
    ):
        """
        构造函数
        :param name: str 名称
        :param shortName: str 短名称
        :param hasGrid: bool 是否有格子
        :param basePrice: int 基础价格
        :param width: int 宽度
        :param height: int 高度
        :param img: str 图片名
        :param category: str 类别
        :param avg24hPrice: int 24小时平均价格
        :param low24hPrice: int 24小时最低价格
        :param high24hPrice: int 24小时最高价格
        :param accuracyModifier: float 精度修正
        :param recoilModifier: float 后坐力修正
        :param ergonomicsModifier: float 人体工学修正
        :param weight: float 重量
        :param sellFor: ItemPrice 出售来源
        :param buyFor: list[ItemPrice] 购买来源
        :param craftsFor: list[Craft] 合成来源
        :param craftsUsing: list[Craft] 使用来源
        :param fleaMarketPrice: int 跳蚤市场最近价格
        """
        self.name = name
        self.shortName = shortName
        self.hasGrid = True if int(hasGrid) == 1 else False
        self.basePrice = basePrice
        self.width = width
        self.height = height
        self.img = img
        self.category = category
        self.avg24hPrice = avg24hPrice
        self.low24hPrice = low24hPrice
        self.high24hPrice = high24hPrice
        self.accuracyModifier = accuracyModifier
        self.recoilModifier = recoilModifier
        self.ergonomicsModifier = ergonomicsModifier
        self.weight = weight
        self.sellFor = sellFor
        self.buyFor = buyFor
        self.craftsFor = craftsFor
        self.craftsUsing = craftsUsing
        self.fleaMarketPrice = fleaMarketPrice


class dbAmmo(Base):
    """
    子弹数据库类
    """
    __tablename__ = 'bulletdata'
    id = Column(INT, Sequence('bulletdata_id_seq'), primary_key=True)
    name = Column(VARCHAR(255))
    caliber = Column(VARCHAR(255))
    weight = Column(FLOAT)
    stackMaxSize = Column(INT)
    tracer = Column(VARCHAR(255))
    tracerColor = Column(VARCHAR(255))
    damage = Column(VARCHAR(255))
    armorDamage = Column(FLOAT)
    fragmentationChance = Column(FLOAT)
    ricochetChance = Column(FLOAT)
    penetrationPower = Column(INT)
    accuracyModifier = Column(FLOAT)
    recoilModifier = Column(FLOAT)
    lightBleedModifier = Column(FLOAT)
    heavyBleedModifier = Column(FLOAT)
    img = Column(VARCHAR(255))
    marketSale = Column(INT)
    apiID = Column(VARCHAR(255))
    projectileCount = Column(INT)
    initialSpeed = Column(FLOAT)
    staminaBurnPerDamage = Column(FLOAT)
