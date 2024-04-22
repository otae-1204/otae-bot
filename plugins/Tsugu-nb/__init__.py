from nonebot import on_message, on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot import get_bot
import tsugu.handler
from utils.message_builder import image,at
import tsugu
from .config import Config
from .handler import submit_car_number_msg, get_enable_carNum_prompt_groups, save_enable_carNum_prompt_groups
import os
import time

bot_h = on_message(priority=1)
enable_carNum_prompt = on_command("开启车牌上传提示")
close_carNum_prompt = on_command("关闭车牌上传提示")

enable_carNum_prompt_groups = get_enable_carNum_prompt_groups()
# Union [PrivateMessageEvent, GroupMessageEvent, Event]
@bot_h.handle()
async def h(event: Event):
    msg = event.get_plaintext()
    bot = get_bot()
    
    # 获取起始时间
    startTime = time.time()

    # 获取信息ID
    msgid = event.get_event_description().split(" ")[1]

    user_id = event.get_user_id()
    group_id = event.get_session_id().split("_")
    channel_id = group_id[1] if group_id[0] == "group" else user_id
    
    result = submit_car_number_msg(msg, user_id)
    if channel_id in enable_carNum_prompt_groups:
        if result in "提交车牌成功" or result.startswith("车牌上传出现错误"):
            await bot_h.finish(Message(f"[CQ:reply,id={msgid}]") + result)
    else:
        pass

    # 检测是否为指令
    # print("检测是否为指令")
    if msg == "":
        return
    
    if msg[0] != "/":
        return
    
    # msg = msg[1:]

    # 调用tsugu的bot函数
    # print("调用tsugu的bot函数")
    result = None
    try:
        print(f"传入数据为:{msg},{user_id},onebot,{channel_id}")
        result = tsugu.bot(str(msg), str(user_id), "onebot", str(channel_id))
    except Exception as e:
        await bot_h.finish(f"Error: {e}")

    # 处理返回结果
    # print("返回结果:", result)
    if result is not None:
        for item in result:
            if item["type"] == "string":
                print(f"[文字信息]\n{item['string']}")
                # await bot_h.finish(item["string"])
                # await bot_h.
                await bot_h.finish(Message(f"[CQ:reply,id={msgid}]") + item["string"])
                
            elif item["type"] == "base64":
                # image_data = base64.b64decode(item["string"])
                # print(f"[图像大小: {len(image_data) / 1024:.2f}KB]")
                # await bot_h.send("正在发送图片，请稍等")
                # await bot_h.finish(image(b64=item["string"]))
                await bot_h.finish(at(user_id) + image(b64=item["string"]) + f"\n[本次用时{round(time.time() - startTime, 2)}秒]")
            else:
                print(item)
    # else:
    #     await bot_h.finish("未知错误")


@enable_carNum_prompt.handle()
async def ECNP_H(event: Event):
    user_id = event.get_user_id()
    group_id = event.get_session_id().split("_")
    channel_id = group_id[1] if group_id[0] == "group" else user_id
    if channel_id in enable_carNum_prompt_groups:
        # await enable_carNum_prompt.finish("车牌上传提示已开启")
        enable_carNum_prompt_groups.append(channel_id)
        await enable_carNum_prompt.finish(Message(f"[CQ:reply,id={event.get_event_description().split(' ')[1]}]") + "车牌上传提示已经开启,请勿重复开启")
    else:
        enable_carNum_prompt_groups.append(channel_id)
        save_enable_carNum_prompt_groups(enable_carNum_prompt_groups)
        await enable_carNum_prompt.finish(Message(f"[CQ:reply,id={event.get_event_description().split(' ')[1]}]") + "车牌上传提示已开启")


@close_carNum_prompt.handle()
async def CCNP_H(event: Event):
    user_id = event.get_user_id()
    group_id = event.get_session_id().split("_")
    channel_id = group_id[1] if group_id[0] == "group" else user_id
    if channel_id in enable_carNum_prompt_groups:
        enable_carNum_prompt_groups.remove(channel_id)
        save_enable_carNum_prompt_groups(enable_carNum_prompt_groups)
        await close_carNum_prompt.finish(Message(f"[CQ:reply,id={event.get_event_description().split(' ')[1]}]") + "车牌上传提示已关闭")
    else:
        await close_carNum_prompt.finish(Message(f"[CQ:reply,id={event.get_event_description().split(' ')[1]}]") + "车牌上传提示已关闭,请勿重复关闭")

def get_Commands() -> list:
    commands = []
    for i in Config.commands:
        commands += i["command_name"]

    return commands

def updateConfig():
    tsugu.config.backend = Config.backend
    tsugu.config.features = Config.features
    tsugu.config.commands = Config.commands
    tsugu.config.server_list = Config.server_list
    tsugu.config.server_name_to_index = Config.server_name_to_index
    tsugu.config.server_index_to_name = Config.server_index_to_name
    tsugu.config.server_index_to_s_name = Config.server_index_to_s_name
    tsugu.config.user_database_path = Config.user_database_path
    tsugu.config.token_name = Config.token_name
    tsugu.config.bandori_station_token = Config.bandori_station_token
    tsugu.config.use_easy_bg = Config.use_easy_bg
    tsugu.config.compress = Config.compress
    tsugu.config.ban_gacha_simulate_group_data = Config.ban_gacha_simulate_group_data
    tsugu.config.proxy_url = Config.proxy_url
    tsugu.config.backend_use_proxy = Config.backend_use_proxy
    tsugu.config.user_data_backend_use_proxy = Config.user_data_backend_use_proxy
    tsugu.config.submit_car_number_use_proxy = Config.submit_car_number_use_proxy
    tsugu.config.verify_player_bind_use_proxy = Config.verify_player_bind_use_proxy
    tsugu.config.car_config = Config.car_config


# 检测data.csv是否存在
if not os.path.exists(Config.data_path):
    print("未找到data.csv，已创建")
    with open(Config.data_path, "w") as f:
        f.write("")

updateConfig()
