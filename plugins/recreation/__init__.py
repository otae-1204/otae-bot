import random, json, datetime, requests, re, os
from nonebot import on_regex
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from configs.path_config import JSON_PATH, IMAGE_PATH
from utils.message_builder import at, image
from nonebot.adapters.onebot.v11 import Message

MarryGroup = on_regex(r"^/娶群友$|^/jrlp$", flags=re.I)
MarryGroupByForce = on_regex(r"^/强娶(.+?)$", priority=5)
Divorce = on_regex(r"^/离婚$", priority=5)

path = JSON_PATH + "recreation/"
imgPath = IMAGE_PATH + "recreation/"

@MarryGroup.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    msgid = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    groupMembers = await bot.get_group_member_list(group_id=groupId)
    date = datetime.date.today().strftime("%Y-%m-%d")
    with open(f"{path}MarryList.json", "r") as f:
        marryList = dict(json.load(f))
    
    if groupId not in marryList.keys():
        marryList[groupId] = {"married": {}, "familyInfo": {}}
    
    if checkTodayMarryByForce(groupId, playerId, date):
        await MarryGroup.finish(Message(f"[CQ:reply,id={msgid}]") + "你今天已经娶过人了!")

    while True:
        partnerId = random.choice(groupMembers)["user_id"]
        if not checkTodayMarry(groupId, partnerId, date): break
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
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    content = re.findall(pattern=r"\[at:qq=(.+?)\]$",string=event.get_plaintext())[0]
    msgId = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    date = datetime.date.today().strftime("%Y-%m-%d")
    if checkTodayMarryByForce(groupId, playerId, date):
        await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天已经娶过人了!")
    if not checkTodayMarry(groupId, content, date):
        with open(f"{path}MarryList.json", "r") as f:
            marryList = dict(json.load(f))
        marryList[groupId]["married"][content] = {"date": date}
        marryList[groupId]["familyInfo"][playerId] = {"partnerId": content, "date": date}
        with open(f"{path}MarryList.json", "w") as f:
            json.dump(marryList, f)
        partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=content))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=content))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=content))["nickname"]
        with open(f"{imgPath}/{content}.jpg", "wb") as f:
            f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={content}&s=640").content)
        await MarryGroupByForce.send(Message(f"[CQ:reply,id={msgId}]") + f"你今天的老婆是\n{partnerName}({content})"+image(img_name=f"{content}.jpg", path=imgPath))
        os.remove(f"{imgPath}/{content}.jpg")
    else:
        await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "今天这个人已经被娶过了!")


@Divorce.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    msgId = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    date = datetime.date.today().strftime("%Y-%m-%d")
    with open(f"{path}MarryList.json", "r") as f:
        marryList = dict(json.load(f))
    if playerId not in marryList[groupId]["familyInfo"].keys():
        await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天还没有娶人!")
    partnerId = marryList[groupId]["familyInfo"][playerId]["partnerId"]
    marryList[groupId]["married"].pop(partnerId)
    marryList[groupId]["familyInfo"].pop(playerId)
    with open(f"{path}MarryList.json", "w") as f:
        json.dump(marryList, f)
    await Divorce.send(Message(f"[CQ:reply,id={msgId}]") + "你和你的现任老婆离婚了!")



# 检查某人今天是否被娶过
def checkTodayMarry(groupId, playerId, date) -> bool:
    with open(f"{path}MarryList.json", "r") as f:
        marryList = dict(json.load(f))
    if groupId not in marryList.keys():
        marryList[groupId] = {"married": {}, "familyInfo": {}}
    if playerId in marryList[groupId]["married"]:
        if marryList[groupId]["married"][playerId]["date"] == date:
            return True
    return False

# 检查某人今天是否娶过人
def checkTodayMarryByForce(groupId, playerId, date) -> bool:
    with open(f"{path}MarryList.json", "r") as f:
        marryList = dict(json.load(f))
    if groupId not in marryList.keys():
        marryList[groupId] = {"married": {}, "familyInfo": {}}
    if playerId in marryList[groupId]["familyInfo"]:
        if marryList[groupId]["familyInfo"][playerId]["date"] == date:
            return True
    return False


# 插件被加载的时候检查资源我文件夹有没有被创建
os.makedirs(path) if not os.path.exists(path) else ...
os.makedirs(imgPath) if not os.path.exists(imgPath) else ...
# 检查存储数据的json是否存在
if not os.path.exists(f"{path}MarryList.json"):
    with open(f"{path}MarryList.json", "a") as f:
        json.dump({}, f)
