from nonebot import on_command, on_message, get_driver
from nonebot.permission import SUPERUSER
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER, PRIVATE_FRIEND
from nonebot.exception import FinishedException
from nonebot.log import logger
from .util import *
from .api import *
from .entity import User
import time
import re

rule = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | PRIVATE_FRIEND

Tsugu = on_message(priority=10)
enable_carNum_prompt = on_command("开启车牌上传提示",permission=rule)
close_carNum_prompt = on_command("关闭车牌上传提示",permission=rule)
config = Config()
server_list_name = [item for sublist in config.server_list.values()
                    for item in sublist]


@Tsugu.handle()
async def _(event: Event):
    msg = event.get_plaintext()
    command_starts = list(get_driver().config.command_start)
    msgid = event.get_event_description().split(" ")[1]
    start_time = time.time()
    group_id = event.get_session_id().split("_")
    channel_id = group_id[1] if group_id[0] == "group" else event.get_user_id()
    
    if is_car(msg):
        # msg 为 312472 测测测q1试试试
        # 获取前五位或者六位数字
        car_id = re.findall(r"^\d{5,6}", msg)[0]
        print(f"车牌号为:{car_id}")
        result = await submit_room_number(car_id, msg, "onebot", event.get_user_id(), "otae")
        if channel_id in config.enable_carNum_prompt_groups and result["status"] == "success":
            await Tsugu.send(MessageSegment.reply(msgid) + "车牌已提交")
        if result["status"] != "success":
            await Tsugu.send(MessageSegment.reply(msgid) + result["data"])

    # print(f"指令头为:{command_starts}")
    # print(f"type:{type(command_starts)}")
    # for i in command_starts:
        # print(f"i:{i},type:{type(i)}")
        
    if msg == "":
        # print("空消息")
        return    
    
    if "" not in command_starts and msg[0] not in command_starts:
        # print("不是指令")
        return
    
    
    result = []
    if "" in command_starts:
        command = is_command(msg[0:].lower())
    else:
        command = is_command(msg[1:].lower())
    print(command)
    if not command["status"]:
        return
    
    user_data = await get_user_data("onebot", event.get_user_id())
    # print(user_data)
    
    if type(user_data) == dict and user_data["status"] == "success":
        print("获取用户数据成功")
        print(user_data["data"])
        user = User(**user_data["data"])
    elif type(user_data) == list:
        await Tsugu.finish(user_data[0]["string"])
    else:
        await Tsugu.finish("未知错误")
    
    
    print(
        f"传入数据为:{command},{event.get_user_id()},onebot,{event.get_session_id()}")
    try:
        match command["command"]:
            case "查询卡面":
                result = await card_illustration(int(command["message"]))
            case "抽卡模拟":
                result = await gacha_simulate(user.server_mode, int(command["message"]))
            case "查询卡池":
                result = await search_gacha(user.default_server, int(command["message"]))
            case "查询活动":
                result = await search_event(user.default_server, command["message"])
            case "查询歌曲":
                result = await search_song(user.default_server, command["message"])
            case "查询歌曲分数表":
                # 检查字符串最后是否符合服务器模式
                if command["message"].endswith(tuple(server_list_name)):
                    result = await song_meta(user.default_server, get_server_index(command["message"][-2:]))
                else:
                    result = await song_meta(user.default_server, 3)
            case "查询角色":
                result = await search_character(user.default_server, command["message"])
            case "查询铺面":
                # song_id = int(command["message"].split(" ")[0])
                song_id = re.findall(
                    r"\d+", command["message"])[0] if re.findall(r"\d+", command["message"]) else None
                difficulty = command["message"].replace(
                    song_id, "").strip() if song_id else None
                if difficulty == "":
                    difficulty = "ex"
                result = await song_chart(user.default_server, song_id, difficulty)
            case "全部预测线":
                # msgs = command["message"].split(" ")
                event_id = re.findall(
                    r"\d+", command["message"])[0] if re.findall(r"\d+", command["message"]) else None
                if command["message"].endswith(tuple(server_list_name)) or command["message"].startswith(tuple(server_list_name)):
                    # 取出msg中的数字
                    server_index = get_server_index(str(command["message"].replace(
                        event_id, ""))) if event_id else get_server_index(command["message"])
                    result = await ycx_all(server_index, event_id)
                else:
                    result = await ycx_all(user.server_mode, event_id)
            case "预测线":
                text = command["message"]
                server_index = user.server_mode
                if command["message"].endswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][-2:])
                    text = command["message"][:-2].rsplit()
                if command["message"].startswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][:2])
                    text = command["message"][2:].lstrip()
                # print("text:", text)
                # print("tpye:", type(text))
                if type(text) == str:
                    msgs = text.split(" ")
                else:
                    msgs = text
                tier = int(msgs[0])
                if len(msgs) == 1:
                    print(f"请求数据为:{server_index},{tier}")
                    result = await ycx(server_index, tier)
                else:
                    print(f"请求数据为:{server_index},{tier},{int(msgs[1])}")
                    result = await ycx(server_index, tier, int(msgs[1]))
            case "历史预测线":
                # print(command["message"])
                text = command["message"]
                server_index = user.server_mode
                if command["message"].endswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][-2:])
                    text = command["message"][:-2].rsplit()
                if command["message"].startswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][:2])
                    text = command["message"][2:].lstrip()
                # print(f"server_index:{server_index}")
                # print(f"msg:{msg},type:{type(msg)}")
                if type(text) == str:
                    msgs = text.split(" ")
                else:
                    msgs = text
                tier = int(msgs[0])
                if len(msgs) == 1:
                    print(f"请求数据为:{server_index},{tier}")
                    result = await lsycx(server_index, tier)
                else:
                    print(f"请求数据为:{server_index},{tier},{int(msgs[1])}")
                    result = await lsycx(server_index, tier, int(msgs[1]))
            case "查询车牌":
                result = await ycm()
            case "查询卡牌":
                server_index_list = [0, 1, 2, 3, 4]
                msg = command["message"]
                if command["message"].endswith(tuple(server_list_name)):
                    server_index_list = [
                        get_server_index(command["message"][-2:])]
                    msg = command["message"][:-2].rsplit()
                if command["message"].startswith(tuple(server_list_name)):
                    server_index_list = [
                        get_server_index(command["message"][:2])]
                    msg = command["message"][2:].lstrip()

                msg = " ".join(msg) if type(msg) == list else msg

                result = await search_card(server_index_list, msg)
            case "绑定玩家":
                # Todo:绑定玩家
                server_mode = get_server_index(command["message"]) if command["message"].endswith(tuple(server_list_name)) else user.server_mode
                result = await bind_player_request("onebot", event.get_user_id(), True, server_mode)
                await Tsugu.finish(MessageSegment.reply(msgid) + f"请将游戏内签名更改为 {result['data']['verifyCode']} 后发送 /验证+玩家ID 进行验证")
            case "解绑玩家":
                # Todo:解绑玩家
                server_mode = get_server_index(command["message"]) if command["message"].endswith(tuple(server_list_name)) else user.server_mode
                result = await bind_player_request("onebot", event.get_user_id(), False, server_mode)
                # print(result)
                await Tsugu.finish(MessageSegment.reply(msgid) + f"请将游戏内签名更改为 {result['data']['verifyCode']} 后发送 /验证+玩家ID 进行验证")
            case "验证":
                server_mode = user.server_mode
                player_id = int(command["message"])
                if command["message"].endswith(tuple(server_list_name)):
                    server_mode = get_server_index(command["message"][-2:])
                    player_id = int(command["message"][:-2].rsplit())
                if command["message"].startswith(tuple(server_list_name)):
                    server_mode = get_server_index(command["message"][:2])
                    player_id = int(command["message"][2:].lstrip())
                result = [{"type": "string", "string": (await bind_player_verification("onebot", event.get_user_id(), player_id, True, server_mode))['data']}]
            case "玩家信息":
                server_mode = get_server_index(command["message"]) if command["message"].endswith(tuple(server_list_name)) else user.server_mode
                result = await search_player(user.server_list[server_mode]["playerId"], server_mode) if user.server_list[server_mode]["playerId"] != 0 else [{"type": "string", "string": "未绑定玩家,请先绑定"}]
            case "查询玩家":
                server_mode = 3
                player_id = command["message"]
                if command["message"].endswith(tuple(server_list_name)):
                    server_mode = get_server_index(command["message"][-2:])
                    player_id = command["message"][:-2].rsplit()
                if command["message"].startswith(tuple(server_list_name)):
                    server_mode = get_server_index(command["message"][:2])
                    player_id = command["message"][2:].lstrip()
                result = await search_player(player_id, server_mode)
            case "设置主服务器":
                # server_mode = get_server_index(command["message"]) if command["message"].endswith(tuple(server_list_name)) else 3
                # server_mode = command["message"].replace("国服", "cn").replace("日服", "jp").replace("台服", "tw").replace("国际服", "en").replace("韩服", "kr")
                # result = await set_server_mode("onebot", event.get_user_id(), str(server_mode))
                # print(result)
                server_str = command["message"]
                server_mode = int(server_str) if server_str.isdigit() else get_server_index(server_str)
                if server_mode == None:
                    result = [{"type": "string", "string": f"服务器{server_str}不存在"}]
                else:
                    result = await change_user_data("onebot", event.get_user_id(), {"server_mode": server_mode})
                if result["status"] == "success":
                    user.server_mode = server_mode
                    result = [{"type": "string", "string": f"设置主服务器为 {config.server_list[str(server_mode)][0]} 成功"}]
                else:
                    result = [{"type": "string", "string": f"设置主服务器失败"}]
            case "设置默认服务器":
                # server_list = command["message"].replace("国服", "cn").replace("日服", "jp").replace("台服", "tw").replace("国际服", "en").replace("韩服", "kr")
                server_list = []
                for i in command["message"].split(" "):
                    # server_list.append(get_server_index(i) if i.endswith(tuple(server_list_name)) else i)
                    if i.isdigit():
                        server_list.append(int(i))
                    elif i in server_list_name:
                        server_list.append(get_server_index(i))
                    else:
                        result = [{"type": "string", "string": f"服务器{i}不存在"}]
                        break
                    # server_list.append(server_index)
                
                result = await change_user_data("onebot", event.get_user_id(), {"default_server": server_list})
                # result = await set_default_server("onebot", event.get_user_id(), server_list)
                if result["status"] == "success":
                    user.default_server = server_list
                    
                    server_str = ""
                    for i in server_list:
                        if type(i) == int:
                            server_str += config.server_list[str(i)][0] + " "
                        else:
                            server_str += i + " "
                    
                    result = [{"type": "string", "string": f"设置默认服务器为 {server_str}成功"}]
                else:
                    result = [{"type": "string", "string": f"设置默认服务器失败"}]
            case "查询默认数据":
                server_list = []
                for i in user.default_server:
                    if type(i) == str:
                        server_list.append(i)
                        continue
                    server_list.append(config.server_list[str(i)][0])
                msg = f"您的主服务器为: {config.server_list[str(user.server_mode)][0]}\n您的默认服务器列表为: {server_list}"
                # result = await get_user_data("onebot", event.get_user_id())
                await Tsugu.finish(MessageSegment.reply(msgid) + msg)
                
    except FinishedException as Fe:
        return
    except Exception as e:
        logger.error(e)
        result = [{"type": "string", "string": "参数错误"}]

    # print(result)
    
    if len(result) == 1:
        if "type" in result[0] and result[0]["type"] == "string":
            await Tsugu.finish(MessageSegment.reply(msgid) + result[0]["string"])
        else:
            base = result[0]["string"]
            # print(f"[图像大小: {len(base) / 1024:.2f}KB]") if isinstance(base, bytes) else None
            await Tsugu.finish(MessageSegment.at(event.get_user_id()) + MessageSegment.image(base if "base64://" in base else "base64://" + base) + f"\n[本次用时{round(time.time() - start_time, 2)}秒]")
    elif len(result) > 1:
        # await Tsugu.send(MessageSegment.at(event.get_user_id())+"信息过多,将分段输出")
        # print(f"信息过多,将分段输出,共{len(result)}段")
        # print(result)
        num = 0
        send_msgs = ""
        for i in result:
            num += 1
            if "type" in i and i["type"] == "string":
                send_msgs+=MessageSegment.reply(msgid) + i["string"]
            else:
                base = i["string"]
                # print(f"[图像大小: {len(base) / 1024:.2f}KB]") if isinstance(base, bytes) else None
                # 当最后一次循环的时候执行用时,不是最后一次则不输出执行用时
                if num == 1:
                    send_msgs+=MessageSegment.at(event.get_user_id())
                send_msgs+=(
                    MessageSegment.image(base if "base64://" in base else "base64://" + base) if num != len(result) else \
                    MessageSegment.image(base if "base64://" in base else "base64://" + base) + f"\n[本次用时{round(time.time() - start_time, 2)}秒]"
                )
        await Tsugu.finish(send_msgs)

@enable_carNum_prompt.handle()
async def _(event: Event):
    group_id = event.get_session_id().split("_")
    channel_id = group_id[1] if group_id[0] == "group" else event.get_user_id()
    
    if channel_id in config.enable_carNum_prompt_groups:
        await enable_carNum_prompt.finish("车牌上传提示功能已开启,请勿重复开启")
    else:
        config.enable_carNum_prompt_groups.append(channel_id)
        config.save()
        await enable_carNum_prompt.finish("开启车牌上传提示功能成功")

@close_carNum_prompt.handle()
async def _(event: Event):
    group_id = event.get_session_id().split("_")
    channel_id = group_id[1] if group_id[0] == "group" else event.get_user_id()
    
    if channel_id in config.enable_carNum_prompt_groups:
        config.enable_carNum_prompt_groups.remove(channel_id)
        config.save()
        await close_carNum_prompt.finish("关闭车牌上传提示成功")
    else:
        await close_carNum_prompt.finish("车牌上传提示功能已关闭,请勿重复关闭")

