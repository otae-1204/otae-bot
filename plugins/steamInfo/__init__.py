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
import re
from utils.logs import LogUtils
require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .models import PlayerSummaries
from .data_source import BindData, SteamInfoData, ParentData
from .steam import get_steam_id, get_steam_users_info, STEAM_ID_OFFSET
from .draw import draw_friends_status, simplize_steam_player_data, image_to_bytes

# logs = LogUtils("steamInfo")
bind = on_command("steambind", aliases={"绑定steam"}, priority=10)
info = on_command("steaminfo", aliases={"steam信息"}, priority=10)
check = on_command("steamcheck", aliases={"查看steam", "查steam","看看steam"}, priority=10)
update_parent_info = on_command("steamupdate", priority=10)
add = on_command("addsteambind",aliases={"添加Steam绑定"}, priority=10, permission=SUPERUSER)
setname = on_command("setname",aliases={"设置昵称"}, priority=10)
setusername = on_command("setusername",aliases={"设置用户昵称"}, priority=10, permission=SUPERUSER)


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

    msg = steam_info_data.compare(parent_id, steam_info["response"])

    print(msg)
    if msg == []:
        return None

    # steam_status_data = [
    #     await simplize_steam_player_data(player, config.proxy)
    #     for player in steam_info["response"]["players"]
    # ]
    # steam_status_data = []
    # user_SteamList = bind_data.get_info(parent_id)
    # for player in steam_info["response"]["players"]:
    #     nickname = None
    #     for i in user_SteamList:
    #         # print(i)
    #         if i["steam_id"] == player["steamid"]:
    #             if "nickname" in i.keys():
    #                 nickname = i["nickname"]
    #                 break
    #             else:
    #                 nickname = None
    #                 break
    #     player_data = await simplize_steam_player_data(player, config.proxy, nickname)
    #     steam_status_data.append(player_data)
    
    
    # parent_avatar, parent_name = parent_data.get(parent_id)

    # image = draw_friends_status(parent_avatar, parent_name, steam_status_data)

    # await bot.send_group_msg(
    #     group_id=parent_id, message=Message("\n".join(msg) + MessageSegment.image(image_to_bytes(image)))
    # )
    # logs.info(f"群号: {parent_id} 的更新信息为: \n{msg}")
    print(f"=-=-=-=-=-=-=-=-=-=-=-\n群号: {parent_id} 的更新信息为: \n{msg}")
    
    await bot.send_group_msg(
        group_id=parent_id, message=Message("\n".join(msg))
    )


@nonebot.get_driver().on_bot_connect
async def init_steam_info():
    for parent_id in bind_data.content:
        steam_ids = bind_data.get_all(parent_id)

        steam_info = await get_steam_users_info(
            steam_ids, config.steam_api_key, config.proxy
        )

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
        print(f"群号: {group_id} 的玩家信息为: {steam_info}")
        await broadcast_steam_info(group_id, steam_info)

        steam_info_data.update(group_id, steam_info["response"])
        steam_info_data.save()
    
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

@info.handle()
async def info_handle(event: GroupMessageEvent):
    parent_id = str(event.group_id)

    if user_data := bind_data.get(parent_id, event.get_user_id()):
        steam_id = user_data["steam_id"]
        steam_friend_code = str(int(steam_id) - STEAM_ID_OFFSET)

        await info.finish(
            f"你的 Steam ID: {steam_id}\n你的 Steam 好友代码: {steam_friend_code}"
        )
    else:
        await info.finish(
            "未绑定 Steam ID, 请使用 “/steambind [Steam ID 或 Steam好友代码]” 绑定 Steam ID"
        )

@check.handle()
async def check_handle(event: GroupMessageEvent, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip() != "":
        return None

    parent_id = str(event.group_id)
    user_id = str(event.get_user_id())
    
    steam_ids = bind_data.get_all(parent_id)

    steam_info = await get_steam_users_info(
        steam_ids, config.steam_api_key, config.proxy
    )

    logger.debug(f"{parent_id} Players info: {steam_info}")

    parent_avatar, parent_name = parent_data.get(parent_id)
    
    # steam_status_data = [
    #     bind_data.get(parent_id, user_id)["nickname"] if "nickname" in bind_data.get(parent_id, user_id).keys() else None
    #     await simplize_steam_player_data(player, config.proxy)
    #     for player in steam_info["response"]["players"]
    # ]
    
    steam_status_data = []
    user_SteamList = bind_data.get_info(parent_id)
    # print(user_SteamList)
    
    for player in steam_info["response"]["players"]:
        nickname = None
        for i in user_SteamList:
            # print(i)
            if i["steam_id"] == player["steamid"]:
                if "nickname" in i.keys() and i["nickname"] != "":
                    nickname = i["nickname"]
                    break
                else:
                    nickname = None
                    break
        player_data = await simplize_steam_player_data(player, config.proxy, nickname)
        steam_status_data.append(player_data)
    # print(steam_status_data)

    image = draw_friends_status(parent_avatar, parent_name, steam_status_data)

    await check.finish(MessageSegment.image(image_to_bytes(image)))

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

    if "nickname" not in user_data.keys():
        user_data["nickname"] = name
        bind_data.save()
        await setname.finish("设置昵称成功")    
    else:
        user_data["nickname"] = name
        bind_data.save()
        await setname.finish("更新昵称成功")    

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
    # print(user_data)
    
    if user_data is None:
        await setusername.finish("请先绑定steam")
    
    if name == "":
        await setusername.finish("请输入昵称")

    if "nickname" not in user_data.keys():
        user_data["nickname"] = name
        bind_data.save()
        await setusername.finish(f"已为群员 {atid} 设置昵称成功")    
    else:
        user_data["nickname"] = name
        bind_data.save()
        await setusername.finish(f"已为群员 {atid} 更新昵称成功")