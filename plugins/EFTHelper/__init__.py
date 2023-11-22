import re
import time

import os
import requests
from nonebot import on_regex, on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

from configs.config import SYSTEM_PROXY
from configs.path_config import IMAGE_PATH, JSON_PATH
from plugins.EFTHelper.buildImg import build_ammo_image, build_ammo_info
from plugins.EFTHelper.db import DatabaseDao, updateAmmoData
from plugins.EFTHelper.object import AmmoMoreInfo, Craft, ItemPrice
from utils.message_builder import image

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
    db = DatabaseDao()
    data = []

    # 判断子弹名称是否为多个
    for name in ammoNames:
        if type(name) == list:
            data += db.selectAmmoByDiverse(name)
        else:
            data += db.selectAmmoByOneCondition(name)

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
                                     timeout=15, proxies=SYSTEM_PROXY)

            # 判断是否成功
            if response.status_code == 200:
                # 获取数据
                resultData = response.json()["data"]["items"][0]

                # 更新缓存文件
                with open(f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json", "a+") as f:
                    tempData = dict(td := f.read()) if td is not None else {}
                    tempData[resultData['name']] = [resultData["basePrice"], resultData["avg24hPrice"],resultData["historicalPrices"][len(resultData["historicalPrices"] - 1)]["price"]]
                    f.write(str(tempData))

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
                with open(f"{JSON_PATH}/EFTBulletTemp/BulletBuyForTemp.json", "a+") as f:
                    tempData = dict(td := f.read()) if td is not None else {}
                    tempDict = {
                        "price" : buyFor[0].price,
                        "currency" : buyFor[0].currency,
                        "priceRUB" : buyFor[0].priceRUB,
                        "source" : buyFor[0].source,
                        "requirements" : buyFor[0].requirements
                    }
                    tempData[(rd := resultData['name'])] = [tempDict] if rd not in tempData.keys() else tempData[rd].append(tempDict)
                    f.write(str(tempData))

                # 更新CraftsFor缓存文件
                with open(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json", "a+") as f:
                    tempData = dict(td := f.read()) if td is not None else {}
                    tempDict = {
                        "station" : craftsFor[0].station,
                        "level" : craftsFor[0].level,
                        "duration" : craftsFor[0].duration,
                        "requiredItems" : {
                            "name" : craftsFor[0].requiredItems[0]["name"],
                            "iconLink" : craftsFor[0].requiredItems[0]["iconLink"],
                            "count" : craftsFor[0].requiredItems[0]["count"]
                        }
                    }
                    tempData[(rd := resultData['name'])] = [tempDict] if rd not in tempData.keys() else tempData[rd].append(tempDict)
                    f.write(str(tempData))

                # 获取跳蚤市场最近价格
                fleaMarketPrice = resultData["historicalPrices"][len(resultData["historicalPrices"]) - 1]["price"]

            # 不成功则使用缓存数据
            else:
                isTempData = True
        # request异常则使用缓存数据
        except Exception as e:
            isTempData = True
            print("=-=" * 20)
            print("Request异常,使用缓存数据:\n", e)
            print("=-=" * 20)

        # 判断是否使用缓存数据      
        if isTempData:
            selectBullet.finish("内部错误") if not os.path.exists(
                f"{JSON_PATH}/EFTBulletTemp/BulletBuyForTemp.json") else ...
            with open(f"{JSON_PATH}/EFTBulletTemp/BulletBuyForTemp.json", "r") as f:
                tempData = dict(td := f.read()) if td is not None else {}
                buyFor = []
                if data[0].name in tempData.keys():
                    for i in tempData[data[0].name]:
                        buyFor.append(
                            ItemPrice(
                                i["price"],
                                i["currency"],
                                i["priceRUB"],
                                i["source"],
                                i["requirements"]
                            )
                        )
                else:
                    buyFor = -1
            selectBullet.finish("内部错误") if not os.path.exists(
                f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json") else ...
            with open(f"{JSON_PATH}/EFTBulletTemp/BulletCraftsForTemp.json", "r") as f:
                tempData = dict(td := f.read()) if td is not None else {}
                if data[0].name in tempData.keys():
                    craftsFor = []
                    for i in tempData[data[0].name]:
                        requiredItems = []
                        requiredItems.append(
                            {
                                "name": i["requiredItems"]["name"],
                                "iconLink": i["requiredItems"]["iconLink"],
                                "count": i["requiredItems"]["count"]
                            }
                        )
                        craftsFor.append(Craft(i["station"], i["level"], i["duration"], requiredItems))
                else:
                    craftsFor = -1
            selectBullet.finish("内部错误") if not os.path.exists(
                f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json") else ...
            with open(f"{JSON_PATH}/EFTBulletTemp/BulletPriceTemp.json", "r") as f:
                tempData = dict(td := f.read()) if td is not None else {}
                if data[0].name in tempData.keys():
                    basePrice = tempData[data[0].name][0]
                    avg24hPrice = tempData[data[0].name][1]
                    fleaMarketPrice = tempData[data[0].name][2]
                else:
                    basePrice = -1
                    avg24hPrice = -1
                    fleaMarketPrice = -1

        if buyFor == -1 or craftsFor == -1:
            # 若没有缓存数据则绘制粗略图
            imgResult = build_ammo_image(data, qqid)

        # 构建详细信息对象
        ammoMoreInfo = AmmoMoreInfo(
            resultData["basePrice"] if basePrice != -1 else basePrice,
            resultData["avg24hPrice"] if avg24hPrice != -1 else avg24hPrice,
            buyFor,
            craftsFor,
            fleaMarketPrice
        )

        # 绘制图片
        imgResult = build_ammo_info(data[0], ammoMoreInfo, qqid)
    else:
        imgResult = build_ammo_image(data, qqid)

    # 判断绘制结果 1:成功 0:无数据 -1:失败
    if imgResult == 1:
        await selectBullet.send(Message(f"[CQ:reply,id={msgid}]") + "您的查询结果如下" + image(
            f"{IMAGE_PATH}/tkf-bullet/img/{qqid}.png") + f"[本次生成用时{round(time.time() - startTime, 2)}秒]")
        os.remove(f"{IMAGE_PATH}/tkf-bullet/img/{qqid}.png")
        return
    elif imgResult == 0:
        await selectBullet.send(Message(f"[CQ:reply,id={msgid}]") + image(f"{IMAGE_PATH}/tkf-bullet/img/无数据.png"))
    else:
        await selectBullet.finish("查询出现问题,请联系开发者修复")


# 更新子弹数据
@updateBullet.handle()
async def hand(event: Event):
    if updateAmmoData() == 1:
        await updateBullet.finish("更新成功")
    else:
        await updateBullet.finish("更新失败")


# 每次启动时检查资源文件夹是否存在
os.makedirs(f"{IMAGE_PATH}/tkf-bullet/img") if not os.path.exists(f"{IMAGE_PATH}/tkf-bullet/img") else ...
os.makedirs(f"{IMAGE_PATH}/tkf-bullet/craft") if not os.path.exists(f"{IMAGE_PATH}/tkf-bullet/craft") else ...
os.makedirs(f"{IMAGE_PATH}/tkf-bullet/bullet") if not os.path.exists(f"{IMAGE_PATH}/tkf-bullet/bullet") else ...
os.makedirs(f"{IMAGE_PATH}/tkf-bullet/item") if not os.path.exists(f"{IMAGE_PATH}/tkf-bullet/item") else ...
os.makedirs(f"{IMAGE_PATH}/tkf-bullet/traders") if not os.path.exists(f"{IMAGE_PATH}/tkf-bullet/traders") else ...
os.makedirs(f"{IMAGE_PATH}/tkf-bullet/UI") if not os.path.exists(f"{IMAGE_PATH}/tkf-bullet/UI") else ...
os.makedirs(f"{JSON_PATH}/EFTBulletTemp") if not os.path.exists(f"{JSON_PATH}/EFTBulletTemp") else ...
