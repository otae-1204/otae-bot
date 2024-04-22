from .config import Config as config
from tsugu.utils import get_user_data, Remote, help_command, match_command, v2_api_command, load_commands_from_config
from tsugu.handler import bot_extra_local_database, bot_extra_remote_server
import re
import urllib3
import datetime
import pytz


def submit_car_number_msg(message, user_id, platform=None):
    # 检查car_config['car']中的关键字
    for keyword in config.car_config["car"]:
        if str(keyword) in message:
            break
    else:
        return "不属于车牌消息"
    # 检查car_config['fake']中的关键字
    for keyword in config.car_config["fake"]:
        if str(keyword) in message:
            # return False
            return "车牌包含屏蔽词"

    pattern = r"^\d{5}(\D|$)|^\d{6}(\D|$)"
    if not re.match(pattern, message):
        # return False
        return "不属于车牌消息"
    
    # 获取用户数据
    try:
        if platform:
            user_data = get_user_data(platform, user_id) if config.user_database_path else Remote.get_user_data(platform, user_id)
            if not user_data['data']['car']:
                # return True
                return "Error: 未知用户"
    except Exception as e:
        # logger.error('unknown user')
        return "Error: 未知用户"
        # 默认不开启关闭车牌，继续提交

    try:
        car_id = message[:6]
        if not car_id.isdigit() and car_id[:5].isdigit():
            car_id = car_id[:5]

        # 构建 URL
        url = f"https://api.bandoristation.com/index.php?function=submit_room_number&number={car_id}&user_id={user_id}&raw_message={message}&source={config.token_name}&token={config.bandori_station_token}"

        if config.submit_car_number_use_proxy:
            http = urllib3.ProxyManager(config.proxy_url, cert_reqs='CERT_NONE')
        else:
            http = urllib3.PoolManager(cert_reqs='CERT_NONE')

        # 发送请求
        response = http.request('GET', url)

        # 检查响应的状态码是否为 200
        if response.status == 200:
            return "提交车牌成功"
        else:
            # logger.error(f"[Tsugu] 提交车牌失败，HTTP响应码: {response.status}")
            # return True  # 虽然提交失败，但是确定了是车牌消息
            return f"提交车牌失败，HTTP响应码: {response.status}"

    except Exception as e:
        # logger.error(f"[Tsugu] 发生异常: {e}")
        # return True  # 虽然提交失败，但是确定了是车牌消息
        return f"车牌上传出现错误: {e}"

# def bot(message, user_id, platform, channel_id):
#     '''
#     不再建议直接使用此函数，请使用 handler 函数
#     :param message:
#     :param user_id:
#     :param platform:
#     :param channel_id:
#     :return:
#     '''
#     try:
#         message = message.strip()

#         # help
#         if config.features.get('help', True):
#             if message.startswith('帮助'):
#                 return help_command()
#             if message.startswith('help'):
#                 arg_text = message[4:].strip()
#                 return help_command(arg_text)
#             if message.endswith('-h'):
#                 arg_text = message[:-2].strip()
#                 return help_command(arg_text)

#         # # 进行车牌匹配
#         # if config.features.get('car_number_forwarding'):
#         #     status = submit_car_number_msg(message, user_id, platform)
#         #     if status:
#         #         return None  # 已经匹配了车牌，就不需要再匹配其他指令了

#         # 进行 v2 api 命令匹配
#         command_matched, api = match_command(message, load_commands_from_config(config.commands))
#         if command_matched:
#             return v2_api_command(message, command_matched, api, platform, user_id, channel_id)
#         if config.user_database_path:
#             return bot_extra_local_database(message, user_id, platform)
#         return bot_extra_remote_server(message, user_id, platform)
#     except Exception as e:
#         print.error(f'Error: {e}')
#         raise e

def get_enable_carNum_prompt_groups() -> list | str: 
    try:
        # 读取./data.csv文件中的群号并转换成list返回,以","分割
        with open(config.data_path, "r") as f:
            return f.read().split(",")
        ...
    except Exception as e:
        return f"Error: {e}"

def save_enable_carNum_prompt_groups(groups:list) ->str:
    try:
        # 将传入的list转换成字符串并写入./data.csv文件
        with open(config.data_path, "w") as f:
            f.write(",".join(groups))
        return "保存成功"
    except Exception as e:
        return f"Error: {e}"

async def timestamp_to_beijing(timestamp):
    timestamp /= 1000
    utc_time = datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = utc_time.astimezone(beijing_tz)
    return beijing_time.replace(tzinfo=None)
