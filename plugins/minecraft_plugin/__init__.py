from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent, GROUP_OWNER, GROUP_ADMIN
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.permission import SuperUser
from configs.config import Plugin_Config
from plugins.minecraft_plugin.data_source import *
from plugins.minecraft_plugin.draw import draw_server_info, draw_server_list
from .ping import ping
import re

permission_group = SuperUser | GROUP_OWNER | GROUP_ADMIN

config = Plugin_Config("minecraft_plugin")

# 判断是否是第一次运行
if config.plugin_content.get("close_group") is None:
    config.plugin_content["close_group"] = []
    config.update()

# 定义命令
open_plugin = on_command(
    "openping", aliases={"Openping", "OPENPING", "open_ping", "Open_Ping"},
    priority=5, block=True, permission=permission_group)
close_plugin = on_command(
    "closeping", aliases={"Closeping", "CLOSEPING", "close_ping", "Close_Ping"},
    priority=5, block=True, permission=permission_group)
server_ping = on_command(
    "ping", aliases={"Ping", "PING", "p"}, priority=5, block=True)
add_server = on_command(
    "addserver", aliases={"Addserver", "ADD_SERVER", "add_server", "as", "Add_Server"}, priority=5, block=True)
add_server_N = on_command(
    "addservernickname", aliases={
        "asnn", "asn", "Addservernickname", "Addservernick", "Addservern", "Addservername", "Addservername"
    }, priority=5, block=True)
remove_server = on_command(
    "removeserver", aliases={
        "Removeserver", "REMOVE_SERVER", "remove_server", "rs", "Remove_Server",
        "delserver", "Delserver", "DEL_SERVER", "del_server", "ds", "Del_Server"
    }, priority=5, block=True)
remove_server_N = on_command(
    "removeservernickname", aliases={
        "rsnn", "rsn", "Removeservernickname", "Removeservernick", "Removeservern", "Removeservername", "Removeservername"
    },priority=5, block=True)
update_server_N = on_command(
    "updateservername", aliases={
        "Updateservername", "UPDATE_SERVER_NAME", "update_server_name", "usn", "Update_Server_Name", "USN", "Usn", 
        "update_name", "Update_Name", "UPDATE_NAME", "updatename", "Updatename", "UPDATE_NAME", "un", "Un", "UN",
        "editname", "Editname", "EDIT_NAME", "edit_name", "en", "Edit_Name", "EN", "En"
    }, priority=5, block=True)
update_server_A = on_command(
    "updateserveraddress", aliases={
        "Updateserveraddress", "UPDATE_SERVER_ADDRESS", "update_server_address", "usa", "Update_Server_Address", "USA",
        "updateaddress", "Updateaddress", "UPDATE_ADDRESS", "update_address", "ua", "Update_Address", "UA", "Ua",
        "editaddress", "Editaddress", "EDIT_ADDRESS", "edit_address", "ea", "Edit_Address", "EA", "Ea"
    }, priority=5, block=True)
ping_list = on_command(
    "pinglist", aliases={"Pinglist", "PING_LIST", "ping_list", "pl", "Ping_List", "PL"}, priority=5, block=True)

# Ping功能代码
@server_ping.handle()
async def handle_server_ping(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]

        # 判断该功能在该群是否启用
        if group_id in config.plugin_content.get("close_group", []):
            return
        
        # 获取输入的消息
        message = cmd_arg.extract_plain_text()
        
        # 获取服务器信息列表
        results = get_server_info_list(message, group_id)

        # # 获取群名称
        # group_name = await bot.get_group_info(group_id=group_id)
        # print(group_name)
        # print(type(group_name))
        # group_name = str(group_name.get("group_name"))
        # if group_name is None:
        #     group_name = "你收藏的服务器"
        # print(group_name)
        # print(group_name)

        # 判断本群回复图片还是文本
        if group_id in config.plugin_content.get("text_group", []):
            # 获取结果消息
            msg = get_result_msg(results)
            await server_ping.finish(msg)
        else:
            # 获取信息
            group_info = await bot.get_group_info(group_id=group_id)
            group_name = group_info.get("group_name")

            
            # 获取结果消息
            msg = get_result_msg(results, type="img", group_name=group_name)
            await server_ping.finish(MessageSegment.image(msg))

        # # 获取结果消息
        # msg = get_result_msg(results,)
        # await server_ping.finish(msg)
    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 获取服务器信息列表
        results = get_server_info_list(message, group_id)

        # 判断本群回复图片还是文本
        if group_id in config.plugin_content.get("text_group", []):
            # 获取结果消息
            msg = get_result_msg(results)
            await server_ping.finish(msg)
        else:            
            # 获取结果消息
            msg = get_result_msg(results, type="img")
            await server_ping.finish(MessageSegment.image(msg))

    # 其他情况
    else:
        return

# 开启Ping功能
@open_plugin.handle()
async def handle_open_plugin(bot: Bot, event: Event):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 判断该功能在该群是否启用
        if group_id in config.plugin_content.get("close_group", []):
            config.plugin_content["close_group"].remove(group_id)
            config.update()
            await open_plugin.finish("已开启Ping功能")
        else:
            await open_plugin.finish("Ping功能已开启,无需重复开启")
    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        await open_plugin.finish("请在群聊中使用该命令")

# 关闭Ping功能
@close_plugin.handle()
async def handle_close_plugin(bot: Bot, event: Event):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 判断该功能在该群是否启用
        if group_id not in config.plugin_content.get("close_group", []):
            config.plugin_content["close_group"].append(group_id)
            config.update()
            await close_plugin.finish("已关闭Ping功能")
        else:
            await close_plugin.finish("Ping功能已关闭,无需重复关闭")
    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        await close_plugin.finish("请在群聊中使用该命令")

# 添加服务器
@add_server.handle()
async def handle_add_server(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 判断是否输入消息
        if not message:
            await add_server.finish("请输入服务器名称和服务器地址")

        # 分割消息
        param = message.split(" ")

        # 判断参数数量并且为2个变量赋值
        if len(param) != 2:
            await add_server.finish("参数数量不正确，请使用</addserver [name] [address]>添加")
        server_name, server_address = param
        # 将空格转义符"_"替换为空格
        server_name = server_name.replace("_", " ")

        # 添加服务器
        if add_group_server(group_id, server_name, server_address):
            await add_server.finish(f"已添加服务器{server_name}")
        else:
            await add_server.finish(f"添加服务器{server_name}失败")
    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 判断是否输入消息
        if not message:
            await add_server.finish("请输入服务器名称和服务器地址")

        # 分割消息
        param = message.split(" ")

        # 判断参数数量并且为2个变量赋值
        if len(param) != 2:
            await add_server.finish("参数数量不正确，请使用</addserver [name] [address]>添加")
        server_name, server_address = param
        # 将空格转义符"_"替换为空格
        server_name = server_name.replace("_", " ")

        # 添加服务器
        if add_group_server(group_id, server_name, server_address):
            await add_server.finish(f"已添加服务器{server_name}")
        else:
            await add_server.finish(f"添加服务器{server_name}失败")
    # 其他情况
    else:
        return

# 移除服务器
@remove_server.handle()
async def handle_remove_server(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 移除服务器
        str = remove_server_operation(group_id, message)
        await remove_server.finish(str)
    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 移除服务器
        str = remove_server_operation(group_id, message)
        await remove_server.finish(str)
    # 其他情况
    else:
        return

# 添加服务器昵称
@add_server_N.handle()
async def handle_add_server_N(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 判断是否输入消息
        if not message:
            await add_server_N.finish("请输入服务器名称和服务器昵称")

        # 分割消息
        param = message.split(" ")

        # 判断参数数量并且为2个变量赋值
        if len(param) != 2:
            await add_server_N.finish("参数数量不正确，请使用</addservernickname [name] [nickname]>添加")
        server_name, server_nickname = param
        # 将空格转义符"_"替换为空格
        server_name = server_name.replace("_", " ")

        # 添加服务器昵称
        if add_server_nickname(group_id, server_name, server_nickname):
            await add_server_N.finish(f"已添加服务器{server_name}的昵称{server_nickname}")
        else:
            await add_server_N.finish(f"添加服务器{server_name}的昵称{server_nickname}失败")
    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 判断是否输入消息
        if not message:
            await add_server_N.finish("请输入服务器名称和服务器昵称")

        # 分割消息
        param = message.split(" ")

        # 判断参数数量并且为2个变量赋值
        if len(param) != 2:
            await add_server_N.finish("参数数量不正确，请使用</addservernickname [name] [nickname]>添加")
        server_name, server_nickname = param
        # 将空格转义符"_"替换为空格
        server_name = server_name.replace("_", " ")

        # 添加服务器昵称
        if add_server_nickname(group_id, server_name, server_nickname):
            await add_server_N.finish(f"已添加服务器{server_name}的昵称{server_nickname}")
        else:
            await add_server_N.finish(f"添加服务器{server_name}的昵称{server_nickname}失败")
    # 其他情况
    else:
        return

# 移除服务器昵称
@remove_server_N.handle()
async def handle_remove_server_N(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 获取要移除的服务器
        if not message:
            await remove_server_N.finish("请输入服务器名称")

        # 判断消息数量是否正确
        if len(message.split(" ")) != 2:
            await remove_server_N.finish("参数数量不正确，指令应为</rsn [servername] [nickname]>")
        
        # 分割消息
        param = message.split(" ")

        # 替换空格转义符
        server_name = param[0].replace("_", " ")
        server_nickname = param[1].replace("_", " ")

        # 移除服务器昵称
        if remove_server_nickname(group_id, server_name, server_nickname):
            await remove_server_N.finish(f"已移除{server_name}的昵称{server_nickname}")
        else:
            await remove_server_N.finish(f"移除{server_name}的昵称{server_nickname}失败")

    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 获取要移除的服务器
        if not message:
            await remove_server_N.finish("请输入服务器名称")

        # 判断消息数量是否正确
        if len(message.split(" ")) != 2:
            await remove_server_N.finish("参数数量不正确，指令应为</rsn [servername] [nickname]>")
        
        # 分割消息
        param = message.split(" ")

        # 替换空格转义符
        server_name = param[0].replace("_", " ")
        server_nickname = param[1].replace("_", " ")

        # 移除服务器昵称
        if remove_server_nickname(group_id, server_name, server_nickname):
            await remove_server_N.finish(f"已移除{server_name}的昵称{server_nickname}")
        else:
            await remove_server_N.finish(f"移除{server_name}的昵称{server_nickname}失败")
    # 其他情况
    else:
        return

# 更新服务器名称
@update_server_N.handle()
async def handle_update_server_N(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 获取要更新的服务器
        if not message:
            await update_server_N.finish("请输入服务器名称")

        # 判断消息数量是否正确
        if len(message.split(" ")) != 2:
            await update_server_N.finish("参数数量不正确，指令应为</usn [oldname] [newname]>")
        
        # 分割消息
        param = message.split(" ")

        # 替换空格转义符
        old_name = param[0].replace("_", " ")
        new_name = param[1].replace("_", " ")

        # 更新服务器名称
        if update_server_name(group_id, old_name, new_name):
            await update_server_N.finish(f"已将{old_name}更新为{new_name}")
        else:
            await update_server_N.finish(f"更新{old_name}为{new_name}失败")

    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 获取要更新的服务器
        if not message:
            await update_server_N.finish("请输入服务器名称")

        # 判断消息数量是否正确
        if len(message.split(" ")) != 2:
            await update_server_N.finish("参数数量不正确，指令应为</usn [oldname] [newname]>")
        
        # 分割消息
        param = message.split(" ")

        # 替换空格转义符
        old_name = param[0].replace("_", " ")
        new_name = param[1].replace("_", " ")

        # 更新服务器名称
        if update_server_name(group_id, old_name, new_name):
            await update_server_N.finish(f"已将{old_name}更新为{new_name}")
        else:
            await update_server_N.finish(f"更新{old_name}为{new_name}失败")

# 更新服务器地址
@update_server_A.handle()
async def handle_update_server_A(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]
        
        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 获取要更新的服务器
        if not message:
            await update_server_A.finish("请输入服务器名称")

        # 判断消息数量是否正确
        if len(message.split(" ")) != 2:
            await update_server_A.finish("参数数量不正确，指令应为</usa [name] [newaddress]>")
        
        # 分割消息
        param = message.split(" ")

        # 替换空格转义符
        server_name = param[0].replace("_", " ")
        new_address = param[1]

        # 更新服务器地址
        if update_server_address(group_id, server_name, new_address):
            await update_server_A.finish(f"已将{server_name}的地址更新为{new_address}")
        else:
            await update_server_A.finish(f"更新{server_name}的地址为{new_address}失败")

    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取输入的消息
        message = cmd_arg.extract_plain_text()

        # 获取要更新的服务器
        if not message:
            await update_server_A.finish("请输入服务器名称")

        # 判断消息数量是否正确
        if len(message.split(" ")) != 2:
            await update_server_A.finish("参数数量不正确，指令应为</usa [name] [newaddress]>")
        
        # 分割消息
        param = message.split(" ")

        # 替换空格转义符
        server_name = param[0].replace("_", " ")
        new_address = param[1]

        # 更新服务器地址
        if update_server_address(group_id, server_name, new_address):
            await update_server_A.finish(f"已将{server_name}的地址更新为{new_address}")
        else:
            await update_server_A.finish(f"更新{server_name}的地址为{new_address}失败")

# 获取服务器列表
@ping_list.handle()
async def handle_ping_list(bot: Bot, event: Event):
    # 判断消息是私聊还是群聊
    # 群聊
    if isinstance(event, GroupMessageEvent):
        # 获取群号
        group_id = event.get_session_id().split("_")[1]

        # 获取服务器列表
        server_list = get_group_serverlist(group_id)

        # 判断是否有服务器
        if len(server_list) == 0:
            await ping_list.finish("该群没有添加服务器")
        
        # 获取服务器列表消息
        msg = "本群关注的服务器列表:\n"
        for server in server_list:
            msg += f"{server['name']}"
            if server.get("nickname") is not None:
                msg += f"({server['nickname']})"
            msg += f": {server['address']}\n"
        await ping_list.finish(msg)
    # 私聊
    elif isinstance(event, PrivateMessageEvent):
        # 获取交互者的QQ号
        group_id = event.get_session_id()

        # 获取服务器列表
        server_list = get_group_serverlist(group_id)

        # 判断是否有服务器
        if len(server_list) == 0:
            await ping_list.finish("该群没有添加服务器")
        
        # 获取服务器列表消息
        msg = "本群关注的服务器列表:\n"
        for server in server_list:
            msg += f"{server['name']}"
            if server.get("nickname") is not None:
                msg += f"({server['nickname']})"
            msg += f": {server['address']}\n"

        await ping_list.finish(msg)
    # 其他情况
    else:
        return

# 获取服务器列表消息
def get_server_list_msg(group_id, type="group") -> str:
    """
    说明:
        获取服务器列表消息
    参数:
        :param group_id: 群号
    返回:
        :return: 服务器列表消息
    """
    # 获取服务器列表
    server_list = get_group_serverlist(group_id)

    # 判断是否有服务器
    if len(server_list) == 0:
        return "该群没有添加服务器" if type == "group" else "你没有添加服务器"
    
    # 获取服务器列表消息
    msg = "本群关注的服务器列表:\n" if type == "group" else "你关注的服务器列表:\n"
    for server in server_list:
        msg += f"{server['name']}"
        if server.get("nickname") is not None:
            msg += f"({server['nickname']})"
        msg += f": {server['address']}\n"

    return msg

# 查询结果转换为消息
def get_result_msg(results: list, type: str = "text", group_name = "你收藏的服务器") -> Message:
    """
    说明:
        获取查询结果消息
    参数:
        :param results: 查询结果列表
        :param type: 返回消息类型
    """
    if type == "img":
        ## todo: 生成图片消息
        img_list = []
        for i in results:
            img_list.append(draw_server_info(i))
        print(img_list)
        return draw_server_list(img_list, group_name)
    else:
        msg = ""
        for result in results:
            msg += f"服务器名称: {result['name']}"
            if result.get("nickname") is not None:
                msg += f"({result['nickname']})"
            msg += "\n"
            msg += f"服务器地址: {result['address']}\n"
            if result["status"] == "success":
                msg += f"游戏版本: {result['data']['game_version']}\n"
                msg += f"是否为原版服务器: {'是' if result['data']['is_vanilla'] else '否'}\n"
                msg += f"玩家数: {result['data']['online_players']}/{result['data']['max_players']}\n"
                motd = result['data']['motd']
                # 通过正则表达式剔除颜色代码
                motd = re.sub(r"\u00a7[0-9a-fA-F]", "", motd)
                # 通过正则表达式剔除§和其后方的字符
                motd = re.sub(r"§.", "", motd)
                msg += f"服务器MOTD: {motd}\n"             
                players = result['data']['players'] if result['data']['players'] else "无在线玩家"   
                msg += f"在线玩家列表: {players}"
                if result != results[-1]:
                    msg += "\n\n"
            else:
                msg += f"服务器状态: {result['data']}"
                if result != results[-1]:
                    msg += "\n\n"
        return Message(msg)
    
# 获取服务器信息列表
def get_server_info_list(message: str, group_id) -> list:
    """
    说明:
        获取服务器信息列表
    参数:
        :param message: 消息
        :param group_id: 群号/QQ号
    返回:
        :return: 服务器信息列表
    """
            # 获取输入的服务器名称或地址
    ping_list = [] 

    if message is not None:
        server_names = message.split(" ")
        ping_list += server_names
    
    # print(ping_list)
    # 获取准备请求的服务器列表
    server_list = []
    if len(ping_list) == 0 or ping_list[0] == "":
        server_list = get_group_serverlist(group_id)
    else:
        for name in ping_list:
            # 如果"."存在则说明是服务器地址
            if "." in name:
                server_list.append({"name": name, "address": name})
            # 否则视为服务器名称
            else:
                server = get_server_address(group_id, name)
                if server is not None:
                    server_list.append(server)
    # print(server_list)

    # 请求服务器
    results = []
    for server in server_list:
        ping_result = ping(server["address"], server["type"])
        results.append({
            "name": server["name"],
            "address": server["address"],
            "nickname": server.get("nickname"),
            "status": ping_result["status"],
            "data": ping_result["data"]
        })
    # print(results)
    return results

# 移除服务器操作
def remove_server_operation(group_id, message):
    param = message.split(" ")
    str = ""
    if len(param) > 1:
        for server_name in param:
            if remove_group_server(group_id, server_name):
                str += f"移除{server_name}成功\n"
            else:
                str += f"移除{server_name}失败\n"
    elif len(param) == 1:
        if remove_group_server(group_id, message):
            str = f"移除{message}成功"
        else:
            str = f"移除{message}失败"
    else:
        return "参数数量不正确，请使用</removeserver [name]>移除"
    return str