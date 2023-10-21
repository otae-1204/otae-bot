import re
from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters import Event
from nonebot.permission import SUPERUSER
from .db import DatabaseDao
from .buildImg import build_ammo_image, build_ammo_info
from utils.message_builder import at, image
from configs.path_config import IMAGE_PATH
import requests, os
from .Ammo import AmmoMoreInfo, CraftsFor, BuyFor

ALL_PERMISSION = GROUP_ADMIN | GROUP_OWNER | SUPERUSER

selectBullet = on_regex(r"^/查子弹(.+?)$|^/eftb(.+?)$", flags=re.I)
updateBullet = on_command("更新子弹", permission=ALL_PERMISSION)
selectBulletArmorDamage = on_regex(r"^/查损甲(.+?)$|^/eftbad(.+?)$",flags=re.I)

caliberEpithet = {
    "7.62": ["762"],
    "5.56": ["556"],
    "12.7": ["127"],
    "4.7": ["47"],
    "7.62x51": ["762x51", ".308", "NATO"]
}


@selectBullet.handle()
async def hand(event: Event):
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
        query_cn = """
{
  items(ids:"{}",lang:zh){
    name #名称
    basePrice #基础价格
    avg24hPrice #24小时平均价格
    buyFor { #购买地点
        price #价格
        currency #货币
        priceRUB #价格
        source #来源
      }
    craftsFor { #合成
        id #合成id
        station {
          name #合成台名称
        }
        level #合成等级
        duration #合成时间
        requiredItems { #合成所需物品
          item {
            name #物品名称
          }
          count #数量
        }
    }
  }
}
""".format(data[0]["apiID"])

        # 浏览器头
        headers = {"Content-Type": "application/json"}

        # 获取中文数据
        response = requests.post('https://api.tarkov.dev/graphql',
                                 json={'query': query_cn}, headers=headers, timeout=30)

        # 判断是否成功
        if response.status_code == 200:
            # 获取数据
            data = response.json()["data"]["items"][0]
            # 获取购买来源
            buyFor = []
            for buy in data["buyFor"]:
                buyFor.append(BuyFor(buy["price"], buy["currency"], buy["priceRUB"], buy["source"]))
            # 获取合成来源
            craftsFor = []
            for craft in data["craftsFor"]:
                requirements = []
                for requirement in craft["requiredItems"]:
                    requirements.append({requirement["item"]["name"]:requirement["count"]})
                craftsFor.append(CraftsFor(craft["station"]["name"], craft["level"], craft["duration"], requirements))

            # 构建详细信息对象
            ammoMoreInfo = AmmoMoreInfo(data["basePrice"], data["avg24hPrice"], buyFor, craftsFor)

            # 绘制图片
            imgResult = (data, ammoMoreInfo, qqid)
        else:
            await selectBullet.finish("查询出现问题,请联系开发者修复")
    else:
        imgResult = build_ammo_image(data, qqid)

    # 判断绘制结果 1:成功 0:无数据 -1:失败
    if imgResult == 1:
        await selectBullet.send(at(qqid) + image(f"{IMAGE_PATH}/tkf-bullet/img/{qqid}.png"))
        os.remove(f"{IMAGE_PATH}/tkf-bullet/{qqid}.png")
        return
    elif imgResult == 0:
        await selectBullet.finish(at(qqid) + image(f"{IMAGE_PATH}/tkf-bullet/img/无数据.png"))
    else:
        await selectBullet.finish("查询出现问题,请联系开发者修复")

@updateBullet.handle()
async def hand(event: Event):
    if db.updateAmmoData() == 1:
        await updateBullet.finish("更新成功")
    else:
        await updateBullet.finish("更新失败")


