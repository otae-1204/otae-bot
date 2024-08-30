from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message
from nonebot.params import CommandArg
from nonebot.log import logger
from configs.config import Plugin_Config
from plugins.minecraft_plugin.data_source import *
from .ping import ping, ServerError
import traceback
# from nonebot_plugin_apscheduler import scheduler

config = Plugin_Config("minecraft_plugin")

server_ping = on_command(
    "ping", aliases={"Ping", "PING", "p"}, priority=5, block=True)
add_server = on_command(
    "addserver", aliases={"Addserver", "ADD_SERVER", "add_server", "as", "Add_Server"}, priority=5, block=True)
remove_server = on_command(
    "removeserver", aliases={
        "Removeserver", "REMOVE_SERVER", "remove_server", "rs", "Remove_Server",
        "delserver", "Delserver", "DEL_SERVER", "del_server", "ds", "Del_Server"
    }, priority=5, block=True)
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


@server_ping.handle()
async def handle_server_ping(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    # 获取群号
    group_id = event.get_session_id().split("_")[1]
    # 获取输入的消息
    message = cmd_arg.extract_plain_text()
    # 判断是否有输入
    if not message:
        server_list = get_group_serverlist(group_id)
        if not server_list:
            await server_ping.finish("当前没有设置服务器,请使用</addserver>添加服务器")

        results = []
        for server in server_list:
            try:
                result = ping(server["address"], server["type"])
                results.append({
                    "name": server["name"],
                    "address": server["address"],
                    "info": result
                })
            except ServerError:
                logger.error(f"查询{server['address']}失败")
                results.append({
                    "name": server["name"],
                    "address": server["address"],
                    "info": "查询失败"
                })
            except Exception as e:
                logger.error(f"查询{server['address']}失败，错误信息：{e}")
                results.append({
                    "name": server["name"],
                    "address": server["address"],
                    "info": "出现未知错误"
                })
        msg = get_result_msg(results)
        await server_ping.finish(msg)
    else:
        server_names = message.split(" ")
        results = []
        for name in server_names:
            # 检测是否包含. 如果包含则直接查询
            if "." in name:
                try:
                    result = ping(name, "java")
                    results.append({
                        "name": name,
                        "address": name,
                        "info": result
                    })
                except ServerError:
                    logger.error(f"查询{name}失败")
                    results.append({
                        "name": name,
                        "address": name,
                        "info": "查询失败"
                    })
                except Exception as e:
                    logger.error(f"查询{name}失败，错误信息：{e}")
                    results.append({
                        "name": name,
                        "address": name,
                        "info": "出现未知错误"
                    })
                server_names.remove(name)

        server_list = [get_server_address(group_id, server_name) for server_name in server_names]
        for server in server_list:
            try:
                result = ping(server["address"], server["type"])
                results.append({
                    "name": server["name"],
                    "address": server["address"],
                    "info": result
                })
            except:
                logger.error(f"查询{server['address']}失败")
                results.append({
                    "name": server["name"],
                    "address": server["address"],
                    "info": "查询失败"
                })
        msg = get_result_msg(results)
        await server_ping.finish(msg)

@add_server.handle()
async def handle_add_server(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    group_id = event.get_session_id().split("_")[1]
    message = cmd_arg.extract_plain_text()
    if not message:
        await add_server.finish("请输入服务器名称和服务器地址")
    param = message.split(" ")
    if len(param) != 2:
        await add_server.finish("参数数量不正确，请使用</addserver [name] [address]>添加")
    server_name, server_address = param
    if add_group_server(group_id, server_name, server_address):
        await add_server.finish(f"已添加服务器{server_name}")
    else:
        await add_server.finish(f"添加服务器{server_name}失败")

@remove_server.handle()
async def handle_remove_server(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    group_id = event.get_session_id().split("_")[1]
    message = cmd_arg.extract_plain_text()

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
        str = "请输入服务器名称"
    await remove_server.finish(str)

@update_server_N.handle()
async def handle_update_server_name(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    group_id = event.get_session_id().split("_")[1]
    message = cmd_arg.extract_plain_text()
    if not message:
        await update_server_N.finish("请输入服务器名称")
    param = message.split(" ")
    if len(param) != 2:
        await update_server_N.finish("参数数量不正确，请使用</usn [old_name] [new_name]>修改")
    old_name, new_name = param
    if update_server_name(group_id, old_name, new_name):
        await update_server_N.finish(f"已将{old_name}修改为{new_name}")
    else:
        await update_server_N.finish(f"修改失败，{old_name}不存在")

@update_server_A.handle()
async def handle_update_server_address(bot: Bot, event: Event, cmd_arg: Message = CommandArg()):
    group_id = event.get_session_id().split("_")[1]
    message = cmd_arg.extract_plain_text()
    if not message:
        await update_server_A.finish("请输入服务器地址")
    param = message.split(" ")
    if len(param) != 2:
        await update_server_A.finish("参数数量不正确，请使用</usa [name] [address]>修改")
    server_name, server_address = param
    if update_server_address(group_id, server_name, server_address):
        await update_server_A.finish(f"已将{server_name}的地址修改为{server_address}")
    else:
        await update_server_A.finish(f"修改失败，{server_name}不存在")

@ping_list.handle()
async def handle_ping_list(bot: Bot, event: Event):
    group_id = event.get_session_id().split("_")[1]
    server_list = get_group_serverlist(group_id)
    if not server_list:
        await ping_list.finish("当前没有设置服务器,请使用</addserver>添加服务器")
    msg = "当前服务器列表：\n"
    for server in server_list:
        msg += f"{server['name']}：{server['address']}\n"
    await ping_list.finish(msg)


# @scheduler.scheduled_job("interval", minutes=60, id="minecraft_plugin")


def get_result_msg(results):
    try:
        # print(results)
        is_simple = False
        if len(results) > 5:
            results = results[:5]
            is_simple = True
        msg = ""
        i = 0
        end = len(results)
        for result in results:
            i += 1
            if result['info'] is None:
                msg += f"服务器名称：{result['name']}\n服务器地址：{result['address']}\n服务器状态：服务器未开启或地址错误\n\n"
                continue
            msg += f"服务器名称：{result['name']}\n服务器地址：{result['address']}\n服务器类型：{result['info']['server_type']}\n"
            if result['info'] == "查询失败":
                msg += "服务器类型错误\n"
            elif result['info'] == "出现未知错误":
                msg += "查询失败\n"
            else:
                msg += f"游戏版本：{result['info']['game_version']}\n"
                msg += f"是否为原版服务器：{'是' if result['info']['is_vanilla'] else '否'}\n"
                msg += f"玩家数：{result['info']['online_players']}/{result['info']['max_players']}\n"
                msg += f"服务器MOTD：{result['info']['motd']}\n"
                msg += f"玩家列表：{' '.join(result['info']['players'])}\n" if result['info']['players'] else "玩家列表：无在线玩家\n"
            if i != end:
                msg += "\n"
            if is_simple and i == 5:
                msg += "仅显示前5个服务器信息,请使用</ping [server_name]>查询其他服务器信息"
        return msg
    except Exception as e:
        traceback.print_exc()
        return f"查询出现错误,错误信息：{e}"


        

