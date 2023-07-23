import re
from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters import Event
from nonebot.permission import SUPERUSER
from .db import DatabaseDao
from .buildImg import build_ammo_image, build_ammo_info
from utils.message_builder import at, image
from configs.path_config import IMAGE_PATH

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
    count = str(event.message).split(" ")[1:]
    print(count)
    print(type(count))
    # print(count)
    # await selectbullet.finish(str(count))
    if count[0] is not None or count[1] is not None:
        qqid = event.get_user_id()
        names = count[0].strip().split(" ") if count[0] is not None else count[1].strip().split(" ")
        for j in names:
            j = j.replace("_", " ")
        db = DatabaseDao()

        for i in range(0,len(names)):
            if "+" in names[i]:
                names[i] = names[i].split("+")
        print(names)
        data = []
        for i in names:
            print(type(i))
            if type(i) == list:
                data += db.selectAmmoByDiverse(i)
            else:
                data += db.selectAmmoByOneCondition(i)
        if len(data) == 1:
            imgResult = build_ammo_info(data[0], qqid)
        else:
            imgResult = build_ammo_image(data, qqid)
        if imgResult == 1:
            await selectBullet.finish(at(qqid) + image(f"{IMAGE_PATH}/tkf-bullet/{qqid}.png"))
        elif imgResult == 0:
            await selectBullet.finish(at(qqid) + image(f"{IMAGE_PATH}/tkf-bullet/无数据.png"))
        else:
            await selectBullet.finish("查询出现问题,请联系开发者修复")

# @selectBulletArmorDamage.handle()
# async def hand(event: Event):
    

@updateBullet.handle()
async def hand(event: Event):
    if db.updateAmmoData() == 1:
        await updateBullet.finish("更新成功")
    else:
        await updateBullet.finish("更新失败")


