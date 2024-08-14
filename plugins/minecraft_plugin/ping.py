from mcstatus import JavaServer, BedrockServer
import re
import base64
# from configs.config import Plugin_Config
from PIL import Image
from io import BytesIO


# 自定义Error
class ServerError(Exception):
    pass


def ping(server_address, server_type):
    """
    获取服务器信息
    :param server_address: 服务器地址
    :param server_type: 服务器类型
    :return: 服务器信息

    服务器信息包括：
    game_version: 游戏版本
    is_vanilla: 是否为原版服务器
    online_players: 在线玩家数
    max_players: 最大玩家数
    motd: 服务器MOTD
    favicon: 服务器图标
    server_type: 服务器类型
    players: 在线玩家列表
    """
    if server_type == 'java':
        server = JavaServer.lookup(server_address)
    elif server_type == 'bedrock':
        server = BedrockServer.lookup(server_address)
    else:
        # 服务器类型错误，抛出异常
        raise ServerError
    try:
        status = vars(server.status())['raw']
        flag = True
        for k, v in status.items():
            if k not in ['version', 'players', 'description', 'favicon', 'onforcesSecureChat', 'previewsChat']:
                flag = False
            else:
                flag = True
        print(status)
        # print(status.items())
        try:
            players = [i["name"] for i in status["players"]["sample"]]
        except:
            players = []

        favicon: str | None = status.get("favicon")

        server_info = {
            "game_version": status['version']['name'],
            "is_vanilla": flag,
            "online_players": status['players']['online'],
            "max_players": status['players']['max'],
            "motd": status['description'] if type(status['description']) == str else status['description'].get('text'),
            "favicon": base64_to_image(favicon) if favicon is not None else None,
            "server_type": server_type,
            "players": players
        }
        return server_info
    except TimeoutError:
        # 服务器超时，抛出异常
        return None


def base64_to_image(base64_str: str) -> Image.Image:
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    return img

ping('1.yamamoto2.net:2010', 'bedrock')