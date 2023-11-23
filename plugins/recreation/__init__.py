import random, json, datetime, requests, re, os
from nonebot import on_regex
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from configs.path_config import JSON_PATH, IMAGE_PATH
from utils.message_builder import at, image
from nonebot.adapters.onebot.v11 import Message

MarryGroup = on_regex(r"^/娶群友$|^/jrlp$", flags=re.I)
MarryGroupByForce = on_regex(r"^/强娶(.+?)$")
Divorce = on_regex(r"^/离婚$")

path = JSON_PATH + "recreation/"
imgPath = IMAGE_PATH + "recreation/"

@MarryGroup.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    msgid = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    groupMembers = await bot.get_group_member_list(group_id=groupId)
    date = datetime.date.today().strftime("%Y-%m-%d")
    marryList = read_json(f"{path}MarryList.json")
    if checkTodayMarryByForce(groupId, playerId, date):
        partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["nickname"]
        with open(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg", "wb") as f:
            f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={marryList[groupId][playerId]['partnerId']}&s=640").content)
        await MarryGroup.send(Message(f"[CQ:reply,id={msgid}]") + f"你今天已经娶过人了!\n你的老婆是\n{partnerName}({marryList[groupId][playerId]['partnerId']})"+image(img_name=f"{marryList[groupId][playerId]['partnerId']}.jpg", path=imgPath))
        os.remove(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg")
        return
    if groupId not in marryList.keys():
        marryList[groupId] = { 
                playerId: {
                    "state" : 0,
                    "updateTime": date,
                    "partnerId": None,
                    "updatableNum": 1 
                }
            }
    while True:
        partnerId = random.choice(groupMembers)["user_id"]
        if not checkTodayMarry(groupId, partnerId, date) and str(partnerId) != str(playerId): break
    if partnerId not in marryList[groupId].keys():
        marryList[groupId][partnerId] = {
            "state" : 0,
            "updateTime": date,
            "partnerId": None,
            "updatableNum": 1 
        }
    if playerId not in marryList[groupId].keys():
        marryList[groupId][playerId] = {
            "state" : 0,
            "updateTime": date,
            "partnerId": None,
            "updatableNum": 1 
        }
    marryList[groupId][partnerId]["state"] = 1
    marryList[groupId][partnerId]["updateTime"] = date
    marryList[groupId][playerId]["partnerId"] = partnerId
    marryList[groupId][playerId]["updateTime"] = date

    write_json(f"{path}MarryList.json", marryList)
    partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["nickname"]
    with open(f"{imgPath}/{partnerId}.jpg", "wb") as f:
        f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={partnerId}&s=640").content)
    await MarryGroup.send(Message(f"[CQ:reply,id={msgid}]") + f"你今天的老婆是\n{partnerName}({partnerId})"+image(img_name=f"{partnerId}.jpg", path=imgPath))
    os.remove(f"{imgPath}/{partnerId}.jpg")


@MarryGroupByForce.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    partnerId = re.findall(pattern=r"\[CQ:at,qq=(.+?)\]",string=str(event.get_message()))
    # print(str(event.get_message()))
    # print(partnerId)
    partnerId = partnerId[0]
    msgId = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    if len(partnerId) == 0:
        await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "你没有@任何人!")
    if partnerId == playerId:
        await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "你不能娶自己!")
    date = datetime.date.today().strftime("%Y-%m-%d")
    marryList = read_json(f"{path}MarryList.json")
    if groupId not in marryList.keys():
        marryList[groupId] = { 
                playerId : {
                    "state" : 0,
                    "updateTime": date,
                    "partnerId": None,
                    "updatableNum": 1 
                }
            }
    if partnerId not in marryList[groupId].keys():
        marryList[groupId][partnerId] = {
            "state" : 0,
            "updateTime": date,
            "partnerId": None,
            "updatableNum": 1 
        }
    if playerId not in marryList[groupId].keys():
        marryList[groupId][playerId] = {
            "state" : 0,
            "updateTime": date,
            "partnerId": None,
            "updatableNum": 1 
        }
    if checkTodayMarryByForce(groupId, playerId, date):
        partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["nickname"]
        with open(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg", "wb") as f:
            f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={marryList[groupId][playerId]['partnerId']}&s=640").content)
        await MarryGroupByForce.send(Message(f"[CQ:reply,id={msgId}]") + f"你今天已经娶过人了!\n你的老婆是\n{partnerName}({marryList[groupId][playerId]['partnerId']})"+image(img_name=f"{marryList[groupId][playerId]['partnerId']}.jpg", path=imgPath))
        os.remove(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg")
        return
    if checkTodayMarry(groupId, partnerId, date):
        await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "今天这个人已经被娶过了!")
    marryList[groupId][playerId]["partnerId"] = partnerId
    marryList[groupId][playerId]["updateTime"] = date
    marryList[groupId][partnerId]["state"] = 1
    marryList[groupId][partnerId]["updateTime"] = date
    write_json(f"{path}MarryList.json", marryList)
    partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["nickname"]
    with open(f"{imgPath}/{partnerId}.jpg", "wb") as f:
        f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={partnerId}&s=640").content)
    await MarryGroupByForce.send(Message(f"[CQ:reply,id={msgId}]") + f"你今天的老婆是\n{partnerName}({partnerId})"+image(img_name=f"{partnerId}.jpg", path=imgPath))
    os.remove(f"{imgPath}/{partnerId}.jpg")



@Divorce.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    msgId = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    date = datetime.date.today().strftime("%Y-%m-%d")
    marryList = read_json(f"{path}MarryList.json")
    if groupId not in marryList.keys():
        marryList[groupId] = { 
                playerId : {
                    "state" : 0,
                    "updateTime": date,
                    "partnerId": None,
                    "updatableNum": 1 
                }
            }
    if playerId not in marryList[groupId].keys():
        await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天还没有娶人!")
    if marryList[groupId][playerId]["partnerId"] == None or marryList[groupId][playerId]["updateTime"] != date:
        await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天还没有娶人!")
    if marryList[groupId][playerId]["updatableNum"] == 0:
        await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天的次数已经用完了!")
    marryList[groupId][playerId]["updatableNum"] -= 1
    partnerId = str(marryList[groupId][playerId]["partnerId"])
    marryList[groupId][partnerId]["state"] = 0
    marryList[groupId][partnerId]["updateTime"] = date
    marryList[groupId][playerId]["partnerId"] = None
    marryList[groupId][playerId]["updateTime"] = date
    write_json(f"{path}MarryList.json", marryList)
    await Divorce.send(Message(f"[CQ:reply,id={msgId}]") + "你和你的现任老婆离婚了!")

    # with open(f"{path}MarryList.json", "r") as f:
    #     marryList = dict(json.load(f))
    # if playerId not in marryList[groupId]["familyInfo"].keys():
    #     await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天还没有娶人!")
    # partnerId = marryList[groupId]["familyInfo"][playerId]["partnerId"]
    # marryList[groupId]["married"].pop(partnerId)
    # marryList[groupId]["familyInfo"].pop(playerId)
    # with open(f"{path}MarryList.json", "w") as f:
    #     json.dump(marryList, f)
    # await Divorce.send(Message(f"[CQ:reply,id={msgId}]") + "你和你的现任老婆离婚了!")


# 检查某人今天是否被娶过
def checkTodayMarry(groupId, playerId, date) -> bool:
    marryList = read_json(f"{path}MarryList.json")
    if groupId not in marryList.keys():
        marryList[groupId] = { 
                playerId : {
                    "state" : 0,
                    "updateTime": date,
                    "partnerId": None,
                    "updatableNum": 1 
                }
            }
        return False
    if playerId in marryList[groupId]:
        if marryList[groupId][playerId]["updateTime"] == date and marryList[groupId][playerId]["state"] == 1:
            return True
    return False

# 检查某人今天是否娶过人
def checkTodayMarryByForce(groupId, playerId, date) -> bool:
    marryList = read_json(f"{path}MarryList.json")
    if groupId not in marryList.keys():
        marryList[groupId] = {
                playerId : {
                    "state" : 0,
                    "updateTime": date,
                    "partnerId": None,
                    "updatableNum": 1 
                }
            }
        return False
    if playerId in marryList[groupId]:
        if marryList[groupId][playerId]["updateTime"] == date and marryList[groupId][playerId]["partnerId"] != None:
            return True
    return False

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

# 插件被加载的时候检查资源我文件夹有没有被创建
os.makedirs(path) if not os.path.exists(path) else ...
os.makedirs(imgPath) if not os.path.exists(imgPath) else ...