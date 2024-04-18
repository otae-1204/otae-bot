import requests
from configs.path_config import IMAGE_PATH
from plugins.EFTHelper.object import Ammo, dbAmmo
import os
from utils.user_agent import get_user_agent
from configs.config import SYSTEM_PROXY, password, user, address
from utils.db import Database
from utils.logs import LogUtils
import traceback


from sqlalchemy import and_, or_
import httpx

log = LogUtils("EFTHelper")

path = IMAGE_PATH + 'EFTHelper/'

query_cn = """
{
    ammo(lang:zh){
        item{
            id #id
            name #名称
            iconLink #图标
            avg24hPrice #24平均价格
        }
  	    weight #重量
        caliber #口径
  	    stackMaxSize #最大堆叠数量
  	    tracer #是否曳光
		tracerColor #曳光颜色
      	damage #肉伤
  	    armorDamage #损甲百分比
     	fragmentationChance #碎弹率
  	    ricochetChance #跳弹率
      	penetrationPower #穿透值
  	    accuracyModifier #精度修正
      	recoilModifier #后座修正
  	    lightBleedModifier #小出血修正
      	heavyBleedModifier #大出血修正
        projectileCount #弹丸数量
        initialSpeed #初速
        staminaBurnPerDamage #消耗体力
  }
}
"""

# 口径查询开头
caliberStart = ["*", "✳", "＊"]

# ID查询开头
idStart = ["#", "＃"]

# 伤害查询开头
damageStart = ["%", "％"]

# 穿甲查询开头
penetrationStart = ["&", "＆"]

# 大于号兼容全角
greaterThan = [">", "＞"]

# 小于号兼容全角
lessThan = ["<", "＜"]

# 等于号兼容全角
equal = ["=", "＝"]

# 口径映射
caliber_mapping = {
    'Caliber556x45NATO': "5.56x45mm",
    'Caliber12g': "12/70",
    'Caliber762x54R': "7.62x54R",
    'Caliber762x39': "7.62x39mm",
    'Caliber40mmRU': "40x46mm",
    'Caliber9x19PARA': "9x19mm",
    'Caliber545x39': "5.45x39mm",
    'Caliber762x25TT': "7.62x25mm",
    'Caliber9x18PM': "9x18mmPM",
    'Caliber9x39': "9x39mm",
    'Caliber762x51': "7.62x51mm",
    'Caliber366TKM': ".366",
    'Caliber9x21': "9x21mm",
    'Caliber20g': "20/70",
    'Caliber46x30': "4.6x30mm",
    'Caliber127x55': "12.7x55mm",
    'Caliber57x28': "5.7x28mm",
    'Caliber1143x23ACP': ".45ACP",
    'Caliber23x75': "23x75mm",
    'Caliber40x46': "40x46mm",
    'Caliber762x35': ".300 AAC Blackout",
    'Caliber86x70': ".338 Lapua Magnum",
    'Caliber9x33R': ".357 Magnum",
    'Caliber26x75': "26x75mm",
    'Caliber68x51': "6.8x51mm"
}


# 通过任务编号查询任务名
async def query_task_name(taskId):
    """
    说明:
        通过任务编号查询任务名
    参数:
        taskId : str
    返回:
        str
    """
    query_task = '{task(id:"' + taskId + '",lang:zh){name}}'
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient(proxies={SYSTEM_PROXY["https"]: httpx.Proxy(url=SYSTEM_PROXY["https"])})as client:
        response = await client.post('https://api.tarkov.dev/graphql', json={'query': query_task}, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            log.info(f"查询任务“{result['data']['task']['name']}”成功")
        else:
            # print(f"请求失败,错误代码{response.status_code}")
            log.error(f"请求失败,错误代码{response.status_code}")
            return -1
        return result["data"]["task"]["name"]


async def clean_name(name_str: str) -> str:
    """
    说明:
        清理和格式化名称字符串.
    参数:
        name_str : [str] 名称字符串
    返回:
        str
    """
    # print("=-=-="*20)
    # print(name_str)
    # print("=-=-="*20)
    name_mapping = {
        "40毫米VOG-25榴弹": "VOG-25榴弹",
        "“Express”": "6.5毫米鹿弹",
        "“Magnum”": "8.5毫米鹿弹",
        "“Poleva-3”": "Poleva-3",
        "“Poleva-6u”": "Poleva-6u",
        "Copper": "Copper Sabot Premier",
        ".50": ".50 BMG",
        "“SuperFormance”": "SuperFormance",
        "Dual": "Dual Sabot",
        "Poleva-6u": "Poleva-6u",
        "Poleva-3u": "Poleva-3u",
    }
    name_list = name_str.replace("独头弹", "").split(" ")
    ammo_Name = ""
    if name_list[0] in name_mapping:
        ammo_Name = name_mapping[name_list[0]]
    elif len(name_list) == 1:
        ammo_Name = name_list[0]
    elif name_list[0] == ".300":
        if name_list[1] == "AAC":
            ammo_Name = " ".join(name_list[3:])
        elif name_list[1] == "BPZ":
            ammo_Name = "BPZ"
        elif name_list[1] == "Blackout":
            ammo_Name = " ".join(name_list[2:])
    elif name_list[0] == ".338":
        if name_list[1] == "Lapua":
            ammo_Name = " ".join(name_list[3:])
        elif name_list[1] == "UPZ":
            ammo_Name = "UPZ"
    elif name_list[0] == ".357":
        ammo_Name = " ".join(name_list[2:])
    elif name_list[1] == "R" or name_list[1] == "毫米":
        ammo_Name = " ".join(name_list[2:])
    else:
        ammo_Name = " ".join(name_list[1:])
    return ammo_Name


async def process_ammo_data(db: Database, ammo_data) -> int:
    """
    说明:       
        处理子弹数据
    参数:
        db : [DatabaseDao] 数据库操作对象       
        ammo_data : [dict] 子弹数据
    返回:
        int
    """
    img_path = ""
    try:
        for i in ammo_data["data"]["ammo"]:
            caliberStr = i["caliber"]
            caliber = caliber_mapping[caliberStr] if caliberStr in caliber_mapping else caliberStr
            name = await clean_name(i["item"]["name"])
            new_ammo = Ammo(
                id=None,
                name=name,
                caliber=caliber,
                weight=i["weight"],
                stackMaxSize=i["stackMaxSize"],
                tracer=i["tracer"],
                tracerColor=i["tracerColor"],
                damage=i["damage"],
                armorDamage=i["armorDamage"],
                fragmentationChance=i["fragmentationChance"],
                penetrationPower=i["penetrationPower"],
                ricochetChance=i["ricochetChance"],
                accuracyModifier=i["accuracyModifier"],
                recoilModifier=i["recoilModifier"],
                lightBleedModifier=i["lightBleedModifier"],
                heavyBleedModifier=i["heavyBleedModifier"],
                img=caliber.replace("毫米", "mm").replace(
                    "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "") + ".png",
                marketSale=1 if i["item"]["avg24hPrice"] > 0 else 0,
                apiID=i["item"]["id"],
                projectileCount=i["projectileCount"],
                initialSpeed=i["initialSpeed"],
                staminaBurnPerDamage=round(i["staminaBurnPerDamage"], 3)
            )

            ammo_id = await A_selectAmmoInDB(new_ammo)
            if ammo_id > 0:
                await db.update_entity_async(
                    dbAmmo, dbAmmo.id == ammo_id,
                    name=new_ammo.name,
                    caliber=new_ammo.caliber,
                    weight=new_ammo.weight,
                    stackMaxSize=new_ammo.stackMaxSize,
                    tracer=new_ammo.tracer,
                    tracerColor=new_ammo.tracerColor,
                    damage=new_ammo.damage,
                    armorDamage=new_ammo.armorDamage,
                    fragmentationChance=new_ammo.fragmentationChance,
                    ricochetChance=new_ammo.ricochetChance,
                    penetrationPower=new_ammo.penetrationPower,
                    accuracyModifier=new_ammo.accuracyModifier,
                    recoilModifier=new_ammo.recoilModifier,
                    lightBleedModifier=new_ammo.lightBleedModifier,
                    heavyBleedModifier=new_ammo.heavyBleedModifier,
                    img=new_ammo.img,
                    marketSale=new_ammo.marketSale,
                    apiID=new_ammo.apiID,
                    projectileCount=new_ammo.projectileCount,
                    initialSpeed=new_ammo.initialSpeed,
                    staminaBurnPerDamage=new_ammo.staminaBurnPerDamage
                )
                # 删除旧图片
                image_path = os.path.join(path, "bullet", caliber.replace("毫米", "mm").replace(
                    "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "") + ".png")
                if os.path.exists(image_path):
                    os.remove(image_path)
                    log.info(f"删除{image_path}成功")
                else:
                    log.warning(f"文件 {image_path} 不存在")
                # 下载新图片
                async with httpx.AsyncClient(proxies={SYSTEM_PROXY["https"]: httpx.Proxy(url=SYSTEM_PROXY["https"])}) as client:
                    response = await client.get(i["item"]["iconLink"], timeout=30)
                    if response.status_code == 200:
                        img_path = caliber.replace("毫米", "mm").replace(
                            "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "")
                        with open(f"{path}/bullet/{img_path}.png", 'wb') as f:
                            f.write(response.content)
                        log.info(f"下载{img_path}成功")
                    else:
                        log.error(f"请求失败,错误代码{response.status_code}")
                        return -1
            else:
                await db.add_entity_async(dbAmmo,
                                          id=None,
                                          name=new_ammo.name,
                                          caliber=new_ammo.caliber,
                                          weight=new_ammo.weight,
                                          stackMaxSize=new_ammo.stackMaxSize,
                                          tracer=new_ammo.tracer,
                                          tracerColor=new_ammo.tracerColor,
                                          damage=new_ammo.damage,
                                          armorDamage=new_ammo.armorDamage,
                                          fragmentationChance=new_ammo.fragmentationChance,
                                          ricochetChance=new_ammo.ricochetChance,
                                          penetrationPower=new_ammo.penetrationPower,
                                          accuracyModifier=new_ammo.accuracyModifier,
                                          recoilModifier=new_ammo.recoilModifier,
                                          lightBleedModifier=new_ammo.lightBleedModifier,
                                          heavyBleedModifier=new_ammo.heavyBleedModifier,
                                          img=new_ammo.img,
                                          marketSale=new_ammo.marketSale,
                                          apiID=new_ammo.apiID,
                                          projectileCount=new_ammo.projectileCount,
                                          initialSpeed=new_ammo.initialSpeed,
                                          staminaBurnPerDamage=new_ammo.staminaBurnPerDamage
                                          )
                # 下载新图片
                async with httpx.AsyncClient(proxies={SYSTEM_PROXY["https"]: httpx.Proxy(url=SYSTEM_PROXY["https"])}) as client:
                    response = await client.get(i["item"]["iconLink"], timeout=30)
                    if response.status_code == 200:
                        img_path = caliber.replace("毫米", "mm").replace(
                            "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "")
                        with open(f"{path}/bullet/{img_path}.png", 'wb') as f:
                            f.write(response.content)
                        log.info(f"下载{img_path}成功")
                    else:
                        log.error(f"请求失败,错误代码{response.status_code}")
                        return -1
        return 1
    except Exception as e:
        log.error("处理子弹数据时出现错误:\n" + str(e))
        log.error(f"{traceback.print_exc()}")
        return -1


async def updateAmmoData() -> int:
    db = Database()
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient(proxies={SYSTEM_PROXY["https"]: httpx.Proxy(url=SYSTEM_PROXY["https"])}) as client:
        response = await client.post('https://api.tarkov.dev/graphql', json={'query': query_cn}, headers=headers, timeout=30)
        if response.status_code == 200:
            cnData = response.json()
            log.info("子弹更新请求成功")
        else:
            log.error(f"请求失败,错误代码{response.status_code}")
    return await process_ammo_data(db, cnData)


async def A_insertAmmo(ammo: Ammo) -> int:
    """
    说明:
        插入一条数据
    参数:
        ammo : [Ammo] 子弹对象
    返回:
        1 = 成功, -1 = 失败
    """
    try:
        db = Database()
        db.add_entity_async(dbAmmo,
                            name=ammo.name,
                            caliber=ammo.caliber,
                            weight=ammo.weight,
                            stackMaxSize=ammo.stackMaxSize,
                            tracer=ammo.tracer,
                            tracerColor=ammo.tracerColor,
                            damage=ammo.damage,
                            armorDamage=ammo.armorDamage,
                            fragmentationChance=ammo.fragmentationChance,
                            ricochetChance=ammo.ricochetChance,
                            penetrationPower=ammo.penetrationPower,
                            accuracyModifier=ammo.accuracyModifier,
                            recoilModifier=ammo.recoilModifier,
                            lightBleedModifier=ammo.lightBleedModifier,
                            heavyBleedModifier=ammo.heavyBleedModifier,
                            img=ammo.img,
                            marketSale=ammo.marketSale,
                            apiID=ammo.apiID,
                            projectileCount=ammo.projectileCount,
                            initialSpeed=ammo.initialSpeed,
                            staminaBurnPerDamage=ammo.staminaBurnPerDamage
                            )
    except Exception as e:
        log.error("错误方法: A_insertAmmo" + "错误原因:" + str(e))
        return -1


async def A_selectAmmoInDB(ammo: Ammo) -> int:
    """
    说明:
        查询子弹是否存在
    参数:
        ammo : [Ammo] 子弹对象
    返回:
        id / -1
    """
    try:
        db = Database()
        result = await db.get_entities_async(dbAmmo, and_(dbAmmo.name == ammo.name, dbAmmo.caliber == ammo.caliber))
        if result is None or len(result) == 0:
            return -1
        else:
            return result[0].id
    except Exception as e:
        log.error("错误方法: A_selectAmmoInDB\n" + "错误原因:" + str(e))
        return -1


async def selectAmmoByOneCondition(condition: str) -> list:
    """
    说明:
        通过单条件查询子弹数据
    参数:
        condition : str
    返回:
        list
    """
    try:
        result = []
        db = Database()
        if condition[:1] in caliberStart:
            sqlEx = "%" + \
                    condition[1:].replace(
                        "*", "x").replace("×", "x").replace("＊", "x") + "%"
            result = await db.get_entities_async(dbAmmo, dbAmmo.caliber.like(sqlEx))
        elif condition[:1] in idStart:
            sqlEx = "%" + condition[1:] + "%"
            result = await db.get_entities_async(dbAmmo, dbAmmo.id == sqlEx)
        elif condition[:1] in damageStart:
            if condition[1:2] in greaterThan:
                if condition[2:3] in equal:
                    sqlEx = condition[3:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.damage >= sqlEx)
                else:
                    sqlEx = condition[2:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.damage > sqlEx)
            elif condition[1:2] in lessThan:
                if condition[2:3] in equal:
                    sqlEx = condition[3:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.damage <= sqlEx)
                else:
                    sqlEx = condition[2:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.damage < sqlEx)
            elif condition[1:2] in equal:
                sqlEx = condition[2:]
                result = await db.get_entities_async(dbAmmo, dbAmmo.damage == sqlEx)
        elif condition[:1] in penetrationStart:
            if condition[1:2] in greaterThan:
                if condition[2:3] in equal:
                    sqlEx = condition[3:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.penetrationPower >= sqlEx)
                else:
                    sqlEx = condition[2:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.penetrationPower > sqlEx)
            elif condition[1:2] in lessThan:
                if condition[2:3] in equal:
                    sqlEx = condition[3:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.penetrationPower <= sqlEx)
                else:
                    sqlEx = condition[2:]
                    result = await db.get_entities_async(dbAmmo, dbAmmo.penetrationPower < sqlEx)
            elif condition[1:2] in equal:
                sqlEx = condition[2:]
                result = await db.get_entities_async(dbAmmo, dbAmmo.penetrationPower == sqlEx)
        else:
            sqlEx = "%" + condition + "%"
            result = await db.get_entities_async(dbAmmo, dbAmmo.name.like(sqlEx))
        ammoList = result
        return ammoList
    except Exception as e:
        log.error("错误方法: selectAmmoByOneCondition\n" + "错误原因:" + str(e))
        return []


async def selectAmmoByDiverse(conditions: list) -> list:
    """
    说明:
        通过多条件查询子弹数据
    参数:
        conditions : list
    返回:
        list
    """
    try:
        result = []
        db = Database()
        and_list = []
        for condition in conditions:
            if condition[:1] in caliberStart:
                sqlEx = "%" + \
                        condition[1:].replace(
                            "*", "x").replace("×", "x").replace("＊", "x") + "%"
                and_list.append(dbAmmo.caliber.like(sqlEx))
            elif condition[:1] in idStart:
                sqlEx = "%" + condition[1:] + "%"
                and_list.append(dbAmmo.id == sqlEx)
            elif condition[:1] in damageStart:
                if condition[1:2] in greaterThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        and_list.append(dbAmmo.damage >= sqlEx)
                    else:
                        sqlEx = condition[2:]
                        and_list.append(dbAmmo.damage > sqlEx)
                elif condition[1:2] in lessThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        and_list.append(dbAmmo.damage <= sqlEx)
                    else:
                        sqlEx = condition[2:]
                        and_list.append(dbAmmo.damage < sqlEx)
                elif condition[1:2] in equal:
                    sqlEx = condition[2:]
                    and_list.append(dbAmmo.damage == sqlEx)
            elif condition[:1] in penetrationStart:
                if condition[1:2] in greaterThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        and_list.append(dbAmmo.penetrationPower >= sqlEx)
                    else:
                        sqlEx = condition[2:]
                        and_list.append(dbAmmo.penetrationPower > sqlEx)
                elif condition[1:2] in lessThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        and_list.append(dbAmmo.penetrationPower <= sqlEx)
                    else:
                        sqlEx = condition[2:]
                        and_list.append(dbAmmo.penetrationPower < sqlEx)
                elif condition[1:2] in equal:
                    sqlEx = condition[2:]
                    and_list.append(dbAmmo.penetrationPower == sqlEx)
            else:
                sqlEx = "%" + condition + "%"
                and_list.append(dbAmmo.name.like(sqlEx))
        result = await db.get_entities_async(dbAmmo, and_(*and_list))
        return result
    except Exception as e:
        log.error("错误方法: selectAmmoByDiverse\n" + "错误原因:" + str(e))
        return []
