from nonebot import on_command, on_message, get_driver
from nonebot.rule import to_me
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from .util import *
from .api import *
from .entity import User
import time


Tsugu = on_message(priority=10)
enable_carNum_prompt = on_command("开启车牌上传提示")
close_carNum_prompt = on_command("关闭车牌上传提示")
config = Config()
server_list_name = [item for sublist in config.server_list.values()
                    for item in sublist]


@Tsugu.handle()
async def _(event: Event):
    msg = event.get_plaintext()
    command_starts = get_driver().config.command_start
    msgid = event.get_event_description().split(" ")[1]
    start_time = time.time()

    if msg == "" or (msg[0] not in command_starts if len(command_starts) != 0 else 1):
        return

    result = []
    command = is_command(msg[1:].lower())
    if not command["status"]:
        return
    user = User(**(await get_user_data("onebot", event.get_user_id()))["data"])
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
                    server_index = get_server_index(command["message"].replace(
                        event_id, "")) if event_id else get_server_index(command["message"])
                    result = await ycx_all(server_index, event_id)
                else:
                    result = await ycx_all(3, event_id)
            case "预测线":
                print(command["message"])
                if command["message"].endswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][-2:])
                    msg = command["message"][:-2].rsplit()
                if command["message"].startswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][:2])
                    msg = command["message"][2:].lstrip()
                print(f"server_index:{server_index}")
                print(f"msg:{msg},type:{type(msg)}")
                if type(msg) == str:
                    msgs = msg.split(" ")
                else:
                    msgs = msg
                print(f"msgs:{msgs}")
                tier = int(msgs[0])
                print(f"tier:{tier}")
                if len(msgs) == 1:
                    print(f"请求数据为:{server_index},{tier}")
                    result = await ycx(server_index, tier)
                else:
                    print(f"请求数据为:{server_index},{tier},{int(msgs[1])}")
                    result = await ycx(server_index, tier, int(msgs[1]))
            case "历史预测线":
                print(command["message"])
                if command["message"].endswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][-2:])
                    msg = command["message"][:-2].rsplit()
                if command["message"].startswith(tuple(server_list_name)):
                    server_index = get_server_index(command["message"][:2])
                    msg = command["message"][2:].lstrip()
                print(f"server_index:{server_index}")
                print(f"msg:{msg},type:{type(msg)}")
                if type(msg) == str:
                    msgs = msg.split(" ")
                else:
                    msgs = msg
                print(f"msgs:{msgs}")
                tier = int(msgs[0])
                print(f"tier:{tier}")
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

    except Exception as e:
        print(e)
        result = [{"type": "string", "string": "参数错误"}]

    if len(result) == 1:
        if "type" in result[0] and result[0]["type"] == "string":
            await Tsugu.finish(MessageSegment.reply(msgid) + result[0]["string"])
        else:
            base = result[0]["string"]
            # print(f"[图像大小: {len(base) / 1024:.2f}KB]") if isinstance(base, bytes) else None
            await Tsugu.finish(MessageSegment.at(event.get_user_id()) + MessageSegment.image(base if "base64://" in base else "base64://" + base) + f"\n[本次用时{round(time.time() - start_time, 2)}秒]")
    elif len(result) > 1:
        await Tsugu.send(MessageSegment.at(event.get_user_id())+"信息过多,将分段输出")
        print(f"信息过多,将分段输出,共{len(result)}段")
        # print(result)
        num = 0
        for i in result:
            num += 1
            if "type" in i and i["type"] == "string":
                await Tsugu.send(MessageSegment.reply(msgid) + i["string"])
            else:
                base = i["string"]
                # print(f"[图像大小: {len(base) / 1024:.2f}KB]") if isinstance(base, bytes) else None
                # 当最后一次循环的时候执行用时,不是最后一次则不输出执行用时
                await Tsugu.send(MessageSegment.at(event.get_user_id()) + MessageSegment.image(base if "base64://" in base else "base64://" + base)) if num != len(result) else \
                    await Tsugu.finish(MessageSegment.at(event.get_user_id()) + MessageSegment.image(base if "base64://" in base else "base64://" + base) + f"\n[本次用时{round(time.time() - start_time, 2)}秒]")
