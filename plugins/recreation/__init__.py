import random, json, datetime, requests, re, os
from nonebot import on_regex
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from configs.path_config import JSON_PATH, IMAGE_PATH
from utils.message_builder import at, image
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.exception import ActionFailed

MarryGroup = on_regex(r"^/娶群友$|^/jrlp$", flags=re.I)
MarryGroupByForce = on_regex(r"^/强娶(.+?)$")
Divorce = on_regex(r"^/离婚$")

path = JSON_PATH + "recreation/"
imgPath = IMAGE_PATH + "recreation/"
updatableNum = 1


@MarryGroup.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    msgid = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    groupMembers = await bot.get_group_member_list(group_id=groupId)
    date = datetime.date.today().strftime("%Y-%m-%d")
    marryList = read_json(f"{path}MarryList.json")
    playerState = checkPlayerState(groupId, playerId, date, marryList)
    if playerState == "已娶":
        try:
            partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["nickname"]
            with open(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg", "wb") as f:
                f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={marryList[groupId][playerId]['partnerId']}&s=640").content)
            await MarryGroup.send(Message(f"[CQ:reply,id={msgid}]") + f"你今天已经娶过人了!\n你的老婆是\n{partnerName}({marryList[groupId][playerId]['partnerId']})"+image(img_name=f"{marryList[groupId][playerId]['partnerId']}.jpg", path=imgPath))
            os.remove(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg")
            return
        except ActionFailed as e:
            marryList[groupId][playerId]["partnerId"] = None
            await MarryGroup.finish(Message(f"[CQ:reply,id={msgid}]") + "这个人不在群里了!")
    if playerState == "已被娶":
        try:
            partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["nickname"]
            with open(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg", "wb") as f:
                f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={marryList[groupId][playerId]['partnerId']}&s=640").content)
            await MarryGroup.send(Message(f"[CQ:reply,id={msgid}]") + f"你今天已经被娶过了!\n你的老公是\n{partnerName}({marryList[groupId][playerId]['partnerId']})"+image(img_name=f"{marryList[groupId][playerId]['partnerId']}.jpg", path=imgPath))
            os.remove(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg")
            return
        except ActionFailed as e:
            marryList[groupId][playerId]["partnerId"] = None
            await MarryGroup.finish(Message(f"[CQ:reply,id={msgid}]") + "这个人不在群里了!")
    if playerState == "未娶":
        partnerId = random.choice(groupMembers)["user_id"]
        while True:
            if checkPlayerState(groupId, partnerId, date, marryList) == "已被娶" or partnerId == playerId or checkPlayerState(groupId, partnerId, date, marryList) == "已娶":
                partnerId = random.choice(groupMembers)["user_id"]
            else:
                break        
        marryList[groupId][playerId]["state"] = 1
        marryList[groupId][playerId]["updateTime"] = date
        marryList[groupId][playerId]["partnerId"] = partnerId
        marryList[groupId][partnerId]["state"] = 2
        marryList[groupId][partnerId]["updateTime"] = date
        marryList[groupId][partnerId]["partnerId"] = playerId
        write_json(f"{path}MarryList.json", marryList)
        try:
            partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["nickname"]
            with open(f"{imgPath}/{partnerId}.jpg", "wb") as f:
                f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={partnerId}&s=640").content)
            await MarryGroup.send(Message(f"[CQ:reply,id={msgid}]") + f"你今天的老婆是\n{partnerName}({partnerId})"+image(img_name=f"{partnerId}.jpg", path=imgPath))
            os.remove(f"{imgPath}/{partnerId}.jpg")
        except ActionFailed as e:
            await MarryGroup.finish(Message(f"[CQ:reply,id={msgid}]") + "这个人不在群里了!")
        return
    else:
        await MarryGroup.finish(Message(f"[CQ:reply,id={msgid}]") + "未知错误!")


@MarryGroupByForce.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    partnerId = re.findall(pattern=r"\[CQ:at,qq=(.+?)\]",string=str(event.get_message()))
    if len(partnerId) == 0:
        await MarryGroupByForce.finish("你没有@任何人!")
    elif len(partnerId) > 1:
        await MarryGroupByForce.finish("你@了多个人!")
    partnerId = partnerId[0]
    msgId = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    if partnerId == playerId:
        await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "你不能娶自己!")
    date = datetime.date.today().strftime("%Y-%m-%d")
    marryList = read_json(f"{path}MarryList.json")
    playerState = checkPlayerState(groupId, playerId, date, marryList)
    if playerState == "已娶":
        try:
            partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["nickname"]
            with open(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg", "wb") as f:
                f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={marryList[groupId][playerId]['partnerId']}&s=640").content)
            await MarryGroupByForce.send(Message(f"[CQ:reply,id={msgId}]") + f"你今天已经娶过人了!\n你的老婆是\n{partnerName}({marryList[groupId][playerId]['partnerId']})"+image(img_name=f"{marryList[groupId][playerId]['partnerId']}.jpg", path=imgPath))
            os.remove(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg")
            return
        except ActionFailed as e:
            marryList[groupId][playerId]["partnerId"] = None
            await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "这个人不在群里了!")
    if playerState == "已被娶":
        try:
            partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=marryList[groupId][playerId]["partnerId"]))["nickname"]
            with open(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg", "wb") as f:
                f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={marryList[groupId][playerId]['partnerId']}&s=640").content)
            await MarryGroupByForce.send(Message(f"[CQ:reply,id={msgId}]") + f"你今天已经被娶过了!\n你的老公是\n{partnerName}({marryList[groupId][playerId]['partnerId']})"+image(img_name=f"{marryList[groupId][playerId]['partnerId']}.jpg", path=imgPath))
            os.remove(f"{imgPath}/{marryList[groupId][playerId]['partnerId']}.jpg")
            return
        except ActionFailed as e:
            marryList[groupId][playerId]["partnerId"] = None
            await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "这个人不在群里了!")
    if playerState == "未娶":
        if checkPlayerState(groupId, partnerId, date, marryList) == "已被娶":
            await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "这个人今天已经被娶过了!")
        marryList[groupId][playerId]["state"] = 1
        marryList[groupId][playerId]["updateTime"] = date
        marryList[groupId][playerId]["partnerId"] = partnerId
        marryList[groupId][partnerId]["state"] = 2
        marryList[groupId][partnerId]["updateTime"] = date
        marryList[groupId][partnerId]["partnerId"] = playerId
        write_json(f"{path}MarryList.json", marryList)
        try:
            partnerName = (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] if (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["card"] != "" else (await bot.get_group_member_info(group_id=groupId, user_id=partnerId))["nickname"]
            with open(f"{imgPath}/{partnerId}.jpg", "wb") as f:
                f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={partnerId}&s=640").content)
            await MarryGroupByForce.send(Message(f"[CQ:reply,id={msgId}]") + f"你今天的老婆是\n{partnerName}({partnerId})"+image(img_name=f"{partnerId}.jpg", path=imgPath))
            os.remove(f"{imgPath}/{partnerId}.jpg")
        except ActionFailed as e:
            await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "这个人不在群里了!")
        return
    else:
        await MarryGroupByForce.finish(Message(f"[CQ:reply,id={msgId}]") + "未知错误!")        


@Divorce.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent):
    msgId = event.get_event_description().split(" ")[1]
    groupId = event.get_session_id().split("_")[1]
    playerId = event.get_user_id()
    date = datetime.date.today().strftime("%Y-%m-%d")
    marryList = read_json(f"{path}MarryList.json")
    playerState = checkPlayerState(groupId, playerId, date, marryList)
    if playerState == "已娶" or playerState == "已被娶":
        if marryList[groupId][playerId]["updatableNum"] == 0 and marryList[groupId][playerId]["updateTime"] == date:
            await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天没有离婚次数了!")
        partnerId = str(marryList[groupId][playerId]["partnerId"])
        marryList[groupId][playerId]["state"] = 0
        marryList[groupId][playerId]["updateTime"] = date
        marryList[groupId][playerId]["partnerId"] = None
        marryList[groupId][partnerId]["state"] = 0
        marryList[groupId][partnerId]["updateTime"] = date
        marryList[groupId][partnerId]["partnerId"] = None
        write_json(f"{path}MarryList.json", marryList)
        marryList[groupId][playerId]["updatableNum"] -= 1
        await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + f"你成功离婚了,你的离婚次数还有{marryList[groupId][playerId]['updatableNum']}次")
    else:
        await Divorce.finish(Message(f"[CQ:reply,id={msgId}]") + "你今天还没结婚呢!")

# 检查某人今天的状态
def checkPlayerState(groupId, playerId, date, marryList) -> str:
    """
    检查某人今天的状态
    :param groupId: 群号
    :param playerId: QQ号
    :param date: 日期
    
    :return: 状态
    """
    if groupId not in marryList.keys():
        marryList[groupId] = { 
                playerId : {
                    "state" : 0,
                    "updateTime": date,
                    "partnerId": None,
                    "updatableNum": updatableNum 
                }
            }
        return "未娶"
    if playerId in marryList[groupId]:
        if marryList[groupId][playerId]["updateTime"] == date and marryList[groupId][playerId]["state"] == 1:
            return "已娶"
        elif marryList[groupId][playerId]["updateTime"] == date and marryList[groupId][playerId]["partnerId"] != None and marryList[groupId][playerId]["state"] == 2:
            return "已被娶"
        else:
            if marryList[groupId][playerId]["updateTime"] != date:
                marryList[groupId][playerId]["state"] = 0
                marryList[groupId][playerId]["updatableNum"] = updatableNum
            return "未娶"
    else:
        marryList[groupId][playerId] = {
            "state" : 0,
            "updateTime": date,
            "partnerId": None,
            "updatableNum": updatableNum
        }
        return "未娶"


# 读取 JSON 文件
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

# 写入 JSON 文件
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

# 插件被加载的时候检查资源文件夹有没有被创建
if not os.path.exists(path):
    os.makedirs(path) 
    write_json(f"{path}MarryList.json", {})
os.makedirs(imgPath) if not os.path.exists(imgPath) else ...