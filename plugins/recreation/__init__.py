import random, json, datetime, requests, re, os
from nonebot import on_regex
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot
from configs.path_config import JSON_PATH, IMAGE_PATH
from utils.message_builder import at, image
from nonebot.adapters.onebot.v11 import Message

MarryGroup = on_regex(r"^/娶群友$|^/jrlp$", flags=re.I)
MarryGroupByForce = on_regex(r"^/强娶(.+?)$", priority=5)

path = JSON_PATH + "recreation/"
imgPath = IMAGE_PATH + "recreation/"

@MarryGroup.handle()
async def handle_first_receive(bot: Bot, event: Event):
    msgid = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    groupMembers = await bot.get_group_member_list(group_id=groupId)
    date = datetime.date.today().strftime("%Y-%m-%d")
    with open(f"{path}MarryList.json", "r") as f:
        marryList = dict(json.load(f))
    
    if groupId not in marryList.keys():
        marryList[groupId] = {"married": {}, "familyInfo": {}}
    
    if playerId in marryList[groupId]["familyInfo"]:
        if marryList[groupId]["familyInfo"][playerId]["date"] == date:
            await MarryGroup.finish("你今天已经有老婆了,不要花心")

    while True:
        partnerId = random.choice(groupMembers)["user_id"]
        if partnerId not in marryList[groupId]["married"].keys():
            break
        elif marryList[groupId]["married"][partnerId]["date"] != date:
            break
    marryList[groupId]["married"][partnerId] = {"date": date}
    marryList[groupId]["familyInfo"][playerId] = {"partnerId": partnerId, "date": date}
    with open(f"{path}MarryList.json", "w") as f:
        json.dump(marryList, f)
    partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["nickname"]
    with open(f"{imgPath}/{partnerId}.jpg", "wb") as f:
        f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={partnerId}&s=640").content)
    await MarryGroup.send(Message(f"[CQ:reply,id={msgid}]") + f"你今天的老婆是\n{partnerName}({partnerId})"+image(img_name=f"{partnerId}.jpg", path=imgPath))
    os.remove(f"{imgPath}/{partnerId}.jpg")


@MarryGroupByForce.handle()
async def handle_first_receive(bot: Bot, event: Event):
    msgId = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()



# 插件被加载的时候检查资源我文件夹有没有被创建
os.makedirs(path) if not os.path.exists(path) else ...
os.makedirs(imgPath) if not os.path.exists(imgPath) else ...
# 检查存储数据的json是否存在
if not os.path.exists(f"{path}MarryList.json"):
    with open(f"{path}MarryList.json", "a") as f:
        json.dump({}, f)
