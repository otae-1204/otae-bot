import aiohttp
import nonebot
from io import BytesIO
from nonebot.log import logger
from PIL import Image as PILImage
from nonebot.params import CommandArg
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
from nonebot.permission import SUPERUSER
import re,time
from utils.message_builder import image as imgMsg
from configs.path_config import IMAGE_PATH
from configs.config import SYSTEM_PROXY
require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .models import PlayerSummaries, Player
from .data_source import BindData, SteamInfoData, ParentData
from .steam import get_steam_id, get_steam_users_info, STEAM_ID_OFFSET
from .draw import draw_friends_status, simplize_steam_player_data, image_to_base64, draw_start_gaming, fetch_avatar, vertically_concatenate_images

# logs = LogUtils("steamInfo")
bind = on_command("steambind", aliases={"绑定steam"}, priority=1)
info = on_command("steaminfo", aliases={"steam信息"}, priority=1)
check = on_command("steamcheck", aliases={"查看steam", "查steam","看看steam"}, priority=1)
update_parent_info = on_command("steamupdate", priority=1)
add = on_command("addsteambind",aliases={"添加Steam绑定"}, priority=1, permission=SUPERUSER)
setname = on_command("setname",aliases={"设置昵称"}, priority=1)
setusername = on_command("setusername",aliases={"设置用户昵称"}, priority=1, permission=SUPERUSER)
unbind = on_command("steamunbind",aliases={"解绑steam"}, priority=1)
unbinduser = on_command("steamunbinduser",aliases={"解绑用户"}, priority=1, permission=SUPERUSER)
delname = on_command("delname",aliases={"删除昵称","unname"}, priority=1)
delusername = on_command("delusername",aliases={"删除用户昵称","unusername"}, priority=1, permission=SUPERUSER)


if hasattr(nonebot, "get_plugin_config"):
    config = nonebot.get_plugin_config(Config)
else:
    from nonebot import get_driver

    config = Config.parse_obj(get_driver().config)


bind_data = BindData("data/steam_info/data.json")
steam_info_data = SteamInfoData("data/steam_info/steam_info.json")
parent_data = ParentData("data/steam_info")


async def broadcast_steam_info(parent_id: str, steam_info: PlayerSummaries):
    bot: Bot = nonebot.get_bot()

    
    # print(parent_list)

    
    
    # steam_info_data.update(parent_id, steam_info["response"])
    # for i in steam_info["response"]["players"]:
    #     ...
    # for i in steam_info["response"]["players"]:
    #     print(i.keys())
    # for i in steam_info["response"]["players"]:
    #     print("传入的steam_info")
    #     print(i.keys())
    
    play_data = steam_info_data.compare(parent_id, steam_info["response"])
    
    msg = []

    for entry in play_data:
        player: Player = entry["player"]
        old_player: Player = entry.get("old_player")
        print(type(entry["player"]["nickname"]))
        
        player_name = entry["player"]["personaname"]
        if entry["player"]["nickname"] is not None and entry["player"]["nickname"].strip() != "":
            player_name = "*" + entry["player"]["nickname"]
        
        if entry["type"] == "start":
            # msg.append(f"{player_name} 开始玩 {player['gameextrainfo']} 了")
            msg.append("¿")
            
        elif entry["type"] == "stop":
            play_time = entry["play_time"]
            msg.append(f"{player_name} 玩了 {play_time} 后停止玩 {old_player['gameextrainfo']} 了")
        elif entry["type"] == "change":
            play_time = entry["play_time"]
            msg.append(
                f"{player_name} 玩了 {play_time} 停止玩 {old_player['gameextrainfo']}，开始玩 {player['gameextrainfo']} 了"
            )
        elif entry["type"] == "error":
            f"出现错误！{player_name}\nNew: {player.get('gameextrainfo')}\nOld: {old_player.get('gameextrainfo')}"
        else:
            logger.error(f"未知的播报类型: {entry['type']}")

    print(msg)
    if msg == []:
        return None
    images = []
    for entry in play_data:
        if entry["type"] == "start":
            nickname = entry["player"]["personaname"]
            if entry["player"]["nickname"] is not None and entry["player"]["nickname"].strip() != "":
                nickname = "*"+entry["player"]["nickname"]
            images.append(
                draw_start_gaming(
                    (
                        await fetch_avatar(
                            entry["player"], 
                            f"{IMAGE_PATH}/steamInfo/cache/", 
                            SYSTEM_PROXY["http"]
                        )
                    ), 
                    nickname, 
                    entry["player"]["gameextrainfo"]
                )
            )
            

    
    send_msg = ""
    for m in msg:
        if m.replace("¿","") != "":
            send_msg += m + ("\n" if msg.index(m) != len(msg) - 1 else "")
    print(send_msg)
    print(len(images))
    # images = [draw_start_gaming((await fetch_avatar(entry["player"], f"{IMAGE_PATH}/steamInfo/cache/", SYSTEM_PROXY["http"])), entry["player"]["personaname"] if entry["player"]["nickname"] is None else entry["player"]["nickname"], entry["player"]["gameextrainfo"]) for entry in play_data if entry["type"] == "start"]
    if images == []:
        await bot.send_group_msg(group_id=parent_id, message=Message(send_msg))
    else:
        image = vertically_concatenate_images(images) if len(images) > 1 else images[0]
        # print(image_to_base64(image))
        await bot.send_group_msg(group_id=parent_id, message=Message(send_msg + imgMsg(b64=image_to_base64(image))))

    # return steam_info
    
    
    # print(f"=-=-=-=-=-=-=-=-=-=-=-\n群号: {parent_id} 的更新信息为: \n{msg}")
    

@nonebot.get_driver().on_bot_connect
async def init_steam_info():
    for parent_id in parent_data.getAll():
        steam_ids = bind_data.get_all(parent_id)

        steam_info = await get_steam_users_info(
            steam_ids, config.steam_api_key, config.proxy
        )
        for i in steam_info["response"]["players"]:
            i["nickname"] = bind_data.get_nickname(parent_id, i["steamid"])
            i["update_time"] = time.time()
        
        steam_info_data.update(parent_id, steam_info["response"])
        steam_info_data.save()



@scheduler.scheduled_job(
    "interval", minutes=config.steam_request_interval / 60, id="update_steam_info"
)
async def update_steam_info():
    # for user_id in bind_data.content.keys():
    for group_id in parent_data.getAll():
        # print(group_id)
        # print(bind_data.get_all(group_id))
        steam_ids = bind_data.get_all(group_id)
        # print(steam_ids)
        # logs.info(f"开始请求群号: {group_id} 的玩家信息")
        print(f"开始请求群号: {group_id} 的玩家信息")
        steam_info = await get_steam_users_info(
            steam_ids, config.steam_api_key, config.proxy
        )
        
        for i in steam_info["response"]["players"]:
            i["nickname"] = bind_data.get_nickname(group_id, i["steamid"])
        
        # print(f"群号: {group_id} 的玩家信息为: {steam_info}")
        await broadcast_steam_info(group_id, steam_info)

        
        # steam_info_data.update(group_id, steam_info["response"])
        # steam_info_data.save()
    
    # for parent_id in bind_data.content:
    #     steam_ids = bind_data.get_all(str(parent_id))
    #     print("=-=-=-=-=-=-=-=-=-=-=-")
    #     print(f"群号: {parent_id} 的玩家信息为: {steam_ids}")

    #     # logs.info(f"开始请求群号: {parent_id} 的玩家信息")
    #     print(f"开始请求群号: {parent_id} 的玩家信息")
    #     steam_info = await get_steam_users_info(
    #         steam_ids, config.steam_api_key, config.proxy
    #     )
    #     print(f"群号: {parent_id} 的玩家信息为: {steam_info}")
    #     await broadcast_steam_info(parent_id, steam_info)

    #     steam_info_data.update(parent_id, steam_info["response"])
    #     steam_info_data.save()


@bind.handle()
async def bind_handle(event: GroupMessageEvent, cmd_arg: Message = CommandArg()):
    parent_id = str(event.group_id)

    arg = cmd_arg.extract_plain_text()

    if not arg.isdigit():
        await bind.finish(
            "请输入正确的 Steam ID 或 Steam好友代码，格式: /steambind [Steam ID 或 Steam好友代码]"
        )

    steam_id = get_steam_id(arg)

    if steam_id in bind_data.get_all(parent_id):
        await bind.finish("该 Steam ID 已绑定")

    if user_data := bind_data.get(parent_id, event.get_user_id()):
        if parent_id in user_data["bindGroups"]:
            user_data["steam_id"] = steam_id
            bind_data.save()

            await bind.finish(f"已更新你的 Steam ID 为 {steam_id}")
        else:
            user_data["bindGroups"].append(
                {
                    "group_id" : parent_id,
                    "nickname" : ""
                }
            )
            bind_data.save()
            await bind.finish(f"已绑定你的 Steam ID 为 {steam_id}")
    else:
        bind_data.add(
            event.get_user_id(),
            {
                "steam_id" : steam_id,
                "bindGroups" : [
                    {
                        "group_id" : parent_id,
                        "nickname" : ""
                    }
                ]
            }
        )
        bind_data.save()

        await bind.finish(f"已绑定你的 Steam ID 为 {steam_id}")

@add.handle()
async def add_handle(event: GroupMessageEvent, cmd_arg: Message = CommandArg()):
    parent_id = str(event.group_id)

    arg = cmd_arg.extract_plain_text().replace(' ','')
    msg = str(event.get_message()).split(' ')[1]

    atid = re.findall(pattern=r"\[CQ:at,qq=(.+?)\]",string=msg)
    print(arg)
    print(atid)
    
    # 正则表达式获取@的qq号
    if not arg.isdigit() or atid == []:
        await add.finish(
            "请输入正确的 Steam ID 或 Steam好友代码，格式: /addsteambind [@某人] [Steam ID 或 Steam好友代码]"
        )
    
    steam_id = get_steam_id(arg)

    if steam_id in bind_data.get_all(parent_id):
        await bind.finish("该 Steam ID 已绑定")
    
    if user_data := bind_data.get(parent_id, atid[0]):
        if parent_id in user_data["bindGroups"]:
            user_data["steam_id"] = steam_id
            bind_data.save()

            await add.finish(f"已更新群员 {atid[0]} 的 Steam ID 为 {steam_id}")
        else:
            user_data["bindGroups"].append(
                {
                    "group_id" : parent_id,
                    "nickname" : ""
                }
            )
            bind_data.save()
            await add.finish(f"已为群员 {atid[0]} 绑定 Steam ID 为 {steam_id}")
    else:
        bind_data.add(
            atid[0],
            {
                "steam_id" : steam_id,
                "bindGroups" : [
                    {
                        "group_id" : parent_id,
                        "nickname" : ""
                    }
                ]
            }
        )
        bind_data.save()
        await add.finish(f"已为群员 {atid[0]} 绑定 Steam ID 为 {steam_id}")

@unbind.handle()
async def unbind_handle(event: GroupMessageEvent):
    parent_id = str(event.group_id)
    user_id = str(event.get_user_id())

    if user_data := bind_data.get(parent_id, user_id):
        if bind_data.delete(parent_id, user_id):
            bind_data.save()
            await unbind.finish("解绑成功")
        else:
            await unbind.finish("解绑失败")
    else:
        await unbind.finish("未绑定 Steam ID")

@info.handle()
async def info_handle(event: GroupMessageEvent):
    parent_id = str(event.group_id)
    
    user_data = bind_data.get(parent_id, event.get_user_id())
    if user_data is None:
        await info.finish(
            "未绑定 Steam ID, 请使用 “/steambind [Steam ID 或 Steam好友代码]” 绑定 Steam ID"
        )
    steam_id = user_data["steam_id"]
    steam_friend_code = str(int(steam_id) - STEAM_ID_OFFSET)
    await info.finish(
        f"你的 Steam ID: {steam_id}\n你的 Steam 好友代码: {steam_friend_code}"
    )
    
    

    # if user_data := bind_data.get(parent_id, event.get_user_id()):
    #     steam_id = user_data["steam_id"]
    #     steam_friend_code = str(int(steam_id) - STEAM_ID_OFFSET)

    #     await info.finish(
    #         f"你的 Steam ID: {steam_id}\n你的 Steam 好友代码: {steam_friend_code}"
    #     )
    # else:
    #     await info.finish(
    #         "未绑定 Steam ID, 请使用 “/steambind [Steam ID 或 Steam好友代码]” 绑定 Steam ID"
    #     )

@check.handle()
async def check_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip() != "":
        return None

    parent_id = str(event.group_id)
    
    steam_ids = bind_data.get_all(parent_id)

    steam_info = await get_steam_users_info(
        steam_ids, config.steam_api_key, config.proxy
    )
    
    for i in steam_info["response"]["players"]:
            i["nickname"] = bind_data.get_nickname(parent_id, i["steamid"])
    # logger.debug(f"{parent_id} Players info: {steam_info}")

    parent_avatar, parent_name = parent_data.get(parent_id)

    steam_status_data = [
    await simplize_steam_player_data(player, SYSTEM_PROXY["http"], f"{IMAGE_PATH}/steamInfo/cache/")
    for player in steam_info["response"]["players"]
    ]

    image = draw_friends_status(parent_avatar, parent_name, steam_status_data)

    await check.finish(imgMsg(b64=image_to_base64(image)))

@update_parent_info.handle()
async def update_parent_info_handle(
    event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()
):
    info = {}
    for seg in arg:
        if seg.type == "image":
            url = seg.data["url"]
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await update_parent_info.finish("获取图片失败")
                    info["avatar"] = PILImage.open(
                        BytesIO(await resp.read())
                    )
        elif seg.is_text() and seg.data["text"] != "":
            info["name"] = seg.data["text"]

    if "avatar" not in info or "name" not in info:
        await update_parent_info.finish("文本中应包含图片和文字")

    parent_data.update(str(event.group_id), info["avatar"], info["name"])
    await update_parent_info.finish("更新成功")

@setname.handle()
async def setname_handle(
    event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()
):
    parent_id = str(event.group_id)
    user_id = str(event.get_user_id())
    name = arg.extract_plain_text().strip()

    user_data = bind_data.get(parent_id, user_id)
    print(user_data)
    
    if user_data is None:
        await setname.finish("请先绑定steam")
    
    if name == "":
        await setname.finish("请输入昵称")

    if len(name) > 16:
        await setname.finish("昵称长度不能超过16个字符")
    
    for i in user_data["bindGroups"]:
        if i["group_id"] == parent_id:
            i["nickname"] = name
            bind_data.save()
            await setname.finish("设置昵称成功")

@setusername.handle()
async def setusername_handle(
    event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()
):
    parent_id = str(event.group_id)
    
    msg = str(event.get_message()).split(' ')[1]
    atid = re.findall(pattern=r"\[CQ:at,qq=(.+?)\]",string=msg)[0]
    print(atid)
    
    name = arg.extract_plain_text().strip()

    user_data = bind_data.get(parent_id, atid)
    print(user_data)
    
    if user_data is None:
        await setusername.finish("请先绑定steam")
    
    if name == "":
        await setusername.finish("请输入昵称")
    
    for i in user_data["bindGroups"]:
        if i["group_id"] == parent_id:
            i["nickname"] = name
            bind_data.save()
            await setusername.finish("设置昵称成功")

@delname.handle()
async def delname_handle(
    event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()
):
    parent_id = str(event.group_id)
    user_id = str(event.get_user_id())
    
    user_data = bind_data.get(parent_id, user_id)
    print(user_data)
    
    if user_data is None:
        await delname.finish("请先绑定steam")
    
    for i in user_data["bindGroups"]:
        if i["group_id"] == parent_id:
            i["nickname"] = ""
            bind_data.save()
            await delname.finish("删除昵称成功")

@delusername.handle()
async def delusername_handle(
    event: GroupMessageEvent, bot: Bot, arg: Message = CommandArg()
):
    parent_id = str(event.group_id)
    
    msg = str(event.get_message()).split(' ')[1]
    atid = re.findall(pattern=r"\[CQ:at,qq=(.+?)\]",string=msg)[0]
    print(atid)
    
    user_data = bind_data.get(parent_id, atid)
    print(user_data)
    
    if user_data is None:
        await delusername.finish("请先绑定steam")
    
    for i in user_data["bindGroups"]:
        if i["group_id"] == parent_id:
            i["nickname"] = ""
            bind_data.save()
            await delusername.finish("删除昵称成功")