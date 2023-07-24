# 子弹信息类
class Ammo:
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
    apiID : str # API ID
    projectileCount : int # 弹丸数量
    initialSpeed : float # 初速
    staminaBurnPerDamage : float # 消耗体力

    # 构造函数
    def __init__(self, id, name, caliber, weight, stackMaxSize, tracer, tracerColor, damage, armorDamage,
                 fragmentationChance, ricochetChance, penetrationPower, accuracyModifier, recoilModifier,
                 lightBleedModifier, heavyBleedModifier, img, marketSale,apiID,projectileCount,initialSpeed,staminaBurnPerDamage):
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
class BuyFor:
    price: int  # 价格
    currency: str  # 货币
    priceRUB: int  # 价格（卢布）
    source: str  # 来源

# 合成来源
class CraftsFor:
    name : str # 名称
    level : int # 等级
    duration : int # 时间
    requirements : list[dict] # 材料 dict(name, count)

# 子弹详细信息类
class AmmoMoreInfo:
    basePrice: int  # 基础价格
    avg24hPrice: int  # 24小时平均价格
    buyFor: list[BuyFor]  # 购买来源
    craftsFor: list[CraftsFor]  # 合成来源