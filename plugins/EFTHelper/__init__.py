import re
import time
import traceback
import os
import requests,json
from nonebot import on_regex, on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

from configs.config import SYSTEM_PROXY
from configs.path_config import IMAGE_PATH, JSON_PATH
from plugins.EFTHelper.buildImg import build_ammo_image, build_ammo_info
from plugins.EFTHelper.db import updateAmmoData, selectAmmoByOneCondition, selectAmmoByDiverse
from plugins.EFTHelper.object import AmmoMoreInfo, Craft, ItemPrice
from utils.message_builder import image
from utils.logs import LogUtils
from utils.db import Database

ALL_PERMISSION = GROUP_ADMIN | GROUP_OWNER | SUPERUSER

selectBullet = on_regex(r"^/查子弹(.+?)$|^/eftb(.+?)$", flags=re.I)
updateBullet = on_command("更新子弹", permission=ALL_PERMISSION)
selectBulletArmorDamage = on_regex(r"^/查损甲(.+?)$|^/eftbad(.+?)$", flags=re.I)

caliberEpithet = {
    "7.62": ["762"],
    "5.56": ["556"],
    "12.7": ["127"],
    "4.7": ["47"],
    "7.62x51": ["762x51", ".308", "NATO"]
}

log = LogUtils("EFTHelper")

# 查询子弹数据
@selectBullet.handle()
async def hand(event: Event):
    # 获取起始时间
    startTime = time.time()

    # 获取信息ID
    msgid = event.get_event_description().split(" ")[1]

    # 获取输入内容
    count = str(event.message).split(" ")[1:]

    # 非空判断
    if len(count) == 0:
        await selectBullet.finish("请输入子弹名称或条件")

    # 获取用户QQ号
    qqid = event.get_user_id()

    # 分割使用交集的查询与替换文本中的"_"为空格
    ammoNames = [name.replace("_", " ").split("+") if "_" in name or "+" in name else name for name in count]

    # 获取数据库对象
    db = Database()
    data = []

    # 判断子弹名称是否为多个
    for name in ammoNames:
        if type(name) == list:
            data += await selectAmmoByDiverse(name)
        else:
            data += await selectAmmoByOneCondition(name)

    print(data)
    # 判断是否绘制详细信息
    if len(data) == 1:
        query_cn = "{ \
    items(ids:\"" + data[0].apiID + "\",lang:zh){ \
    name \
    basePrice \
    avg24hPrice \
    historicalPrices{ \
      price \
    } \
    buyFor { \
        price \
        currency \
        priceRUB \
        source \
        requirements{ \
            value \
            stringValue \
        } \
      }\
    craftsFor { \
        id \
        station {\
          name \
        }\
        level \
        duration \
        requiredItems { \
          item {\
            name \
            iconLink \
          }\
          count \
        }\
    }\
  }\
}\
"

        # 浏览器头
        headers = {"Content-Type": "application/json"}
        isTempData = False
        basePrice = 0
        avg24hPrice = 0
        try:
            # 获取中文数据
            response = requests.post('https://api.tarkov.dev/graphql', json={'query': query_cn}, headers=headers,
                                     timeout=15, proxies={"http" : SYSTEM_PROXY})

            # 判断是否成功
            if response.status_code == 200:
                # 获取数据
                resultData = response.json()["data"]["items"][0]
                fleaMarketPrice = 0
                # 更新缓存文件
                td = read_json(f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json")
                tempData = td if td is not None else {}
                index = len(resultData["historicalPrices"]) - 1
                fleaMarketPrice = resultData["historicalPrices"][index]["price"] if index >= 0 else resultData["basePrice"]
                tempData[resultData['name']] = [resultData["basePrice"], resultData["avg24hPrice"],fleaMarketPrice]
                write_json(f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json", tempData)

                # 获取购买来源
                buyFor = []
                for buy in resultData["buyFor"]:
                    buyFor.append(
                        ItemPrice(
                            buy["price"],
                            buy["currency"],
                            buy["priceRUB"],
                            buy["source"],
                            buy["requirements"]
                        )
                    )

                # 获取合成来源
                craftsFor = []
                for craft in resultData["craftsFor"]:
                    requiredItems = []
                    for item in craft["requiredItems"]:
                        requiredItems.append(
                            {
                                "name": item["item"]["name"],
                                "iconLink": item["item"]["iconLink"],
                                "count": item["count"]
                            }
                        )
                    craftsFor.append(Craft(craft["station"]["name"], craft["level"], craft["duration"], requiredItems))

                # 更新BuyFor缓存文件
                td = read_json(f"{JSON_PATH}/EFTBulletTemp/BulletBuyForTemp.json")
                tempData = td if td is not None else {}
                tempDict = []
                if len(buyFor) != 0:
                    for i in buyFor:
                        tempDict.append({
                            "price" : i.price,
                            "currency" : i.currency,
                            "priceRUB" : i.priceRUB,
                            "source" : i.source,
                            "requirements" : i.requirements
                        })
                else:
                    tempDict = []
                tempData[resultData['name']] = tempDict
                write_json(f"{JSON_PATH}/EFTBulletTemp/BulletBuyForTemp.json", tempData)

                # 更新CraftsFor缓存文件
                td = read_json(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json")
                tempData = td if td is not None else {}
                tempDict = []
                if len(craftsFor) != 0:
                    for i in craftsFor:
                        requiredItems = []
                        for item in i.requirements:
                            requiredItems.append(
                            {
                                "name": item["name"],
                                "iconLink": item["iconLink"],
                                "count": item["count"]
                            }
                        )
                        tempDict.append({
                            "name" : i.name,
                            "level" : i.level,
                            "duration" : i.duration,
                            "requiredItems" : requiredItems
                        })
                else:
                    tempDict = []
                tempData[resultData["name"]] = tempDict
                write_json(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json", tempData)

            # 不成功则使用缓存数据
            else:
                isTempData = True
        # request异常则使用缓存数据
        except Exception as e:
            log.error("Request异常,使用缓存数据:\n" + traceback.format_exc())

        # 判断是否使用缓存数据 
        try:    
            noneTempData = False
            if isTempData:
                td = read_json(f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json")
                tempData = td if td is not None else {}
                if data[0].name in tempData.keys():
                    basePrice = tempData[data[0].name][0]
                    avg24hPrice = tempData[data[0].name][1]
                    fleaMarketPrice = tempData[data[0].name][2]
                    
                else:
                    noneTempData = True

                td = read_json(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json")
                tempData = td if td is not None else {}
                buyFor = []
                for buy in tempData[data[0].name][0]:
                    buyFor.append(
                        ItemPrice(
                            buy["price"],
                            buy["currency"],
                            buy["priceRUB"],
                            buy["source"],
                            buy["requirements"]
                        )
                    )
                else:
                    noneTempData = True
                
                td = read_json(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json")
                tempData = td if td is not None else {}
                craftsFor = []
                if data[0].name in tempData.keys():
                    for i in tempData[data[0].name]:
                        requiredItems = []
                        for item in i["requiredItems"]:
                            requiredItems.append(
                            {
                                "name": item["name"],
                                "iconLink": item["iconLink"],
                                "count": item["count"]
                            }
                        )
                        craftsFor.append(Craft(i["station"], i["level"], i["duration"], requiredItems))
                else:
                    noneTempData = True

        except Exception as e:
            log.error("读取缓存数据异常:\n" + traceback.format_exc())
            noneTempData = True
        
        if noneTempData:
            # 若没有缓存数据则绘制粗略图
            imgResult = build_ammo_image(data, qqid)
        else:
            # 构建详细信息对象
            ammoMoreInfo = AmmoMoreInfo(
                resultData["basePrice"] if basePrice != -1 else basePrice,
                resultData["avg24hPrice"] if avg24hPrice != -1 else avg24hPrice,
                buyFor,
                craftsFor,
                fleaMarketPrice
            )
            # 绘制图片
            imgResult = await build_ammo_info(data[0], ammoMoreInfo, qqid)
    else:
        imgResult = build_ammo_image(data, qqid)

    # 判断绘制结果 1:成功 0:无数据 -1:失败
    if imgResult == 1:
        await selectBullet.send(Message(f"[CQ:reply,id={msgid}]") + "您的查询结果如下" + image(
            f"{IMAGE_PATH}EFTHelper/img/{qqid}.png") + f"[本次生成用时{round(time.time() - startTime, 2)}秒]")
        os.remove(f"{IMAGE_PATH}EFTHelper/img/{qqid}.png")
        return
    elif imgResult == 0:
        await selectBullet.send(Message(f"[CQ:reply,id={msgid}]") + image(f"{IMAGE_PATH}EFTHelper/img/无数据.png"))
    else:
        log.error("绘制图片失败")
        await selectBullet.finish("查询出现问题,请联系开发者修复")


# 更新子弹数据
@updateBullet.handle()
async def hand(event: Event):
    if await updateAmmoData() == 1:
        await updateBullet.finish("更新成功")
    else:
        await updateBullet.finish("更新失败")


def read_json(file_path, create_if_not_exists=True):
    """
    读取 JSON 文件并返回字典，如果文件不存在则创建新文件
    :param file_path: 文件路径
    :param create_if_not_exists: 如果文件不存在是否创建，默认为 True
    :return: 字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        if create_if_not_exists:
            print(f"File '{file_path}' not found. Creating a new file.")
            write_json(file_path, {})  # 创建新文件并写入空字典
            return {}
        else:
            print(f"Error: File '{file_path}' not found.")
            return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file '{file_path}': {e}")
        return None

def write_json(file_path, data):
    """
    将字典写入 JSON 文件
    :param file_path: 文件路径
    :param data: 要写入的字典
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
        print(f"Data written to '{file_path}' successfully.")
    except json.JSONDecodeError as e:
        print(f"Error encoding JSON data: {e}")




# 每次启动时检查资源文件夹是否存在
os.makedirs(f"{IMAGE_PATH}/EFTHelper/img") if not os.path.exists(f"{IMAGE_PATH}/EFTHelper/img") else ...
os.makedirs(f"{IMAGE_PATH}/EFTHelper/craft") if not os.path.exists(f"{IMAGE_PATH}/EFTHelper/craft") else ...
os.makedirs(f"{IMAGE_PATH}/EFTHelper/bullet") if not os.path.exists(f"{IMAGE_PATH}/EFTHelper/bullet") else ...
os.makedirs(f"{IMAGE_PATH}/EFTHelper/item") if not os.path.exists(f"{IMAGE_PATH}/EFTHelper/item") else ...
os.makedirs(f"{IMAGE_PATH}/EFTHelper/traders") if not os.path.exists(f"{IMAGE_PATH}/EFTHelper/traders") else ...
os.makedirs(f"{IMAGE_PATH}/EFTHelper/UI") if not os.path.exists(f"{IMAGE_PATH}/EFTHelper/UI") else ...
os.makedirs(f"{JSON_PATH}/EFTBulletTemp") if not os.path.exists(f"{JSON_PATH}/EFTBulletTemp") else ...
if not os.path.exists(f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json"):
    with open(f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json", "w") as f:
        f.write("{}")
if not os.path.exists(f"{JSON_PATH}/EFTBulletTemp/BulletBuyForTemp.json"):
    with open(f"{JSON_PATH}/EFTBulletTemp/BulletBuyForTemp.json", "w") as f:
        f.write("{}")
if not os.path.exists(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json"):
    with open(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json", "w") as f:
        f.write("{}")

