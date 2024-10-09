from mcstatus import JavaServer, BedrockServer
import re
import base64
from PIL import Image
from io import BytesIO
import traceback

def ping(server_address: str, server_type: str = "java") -> dict:
    """
    获取服务器信息
    :param server_address: str - 服务器地址
    :param server_type: str - 服务器类型
    :return: dict - 服务器信息

    服务器信息包括：
    game_version: str - 游戏版本
    is_vanilla: bool - 是否为原版服务器
    online_players: int - 在线玩家数
    max_players: int - 最大玩家数
    motd: str - 服务器MOTD
    favicon: PIL | None - 服务器图标
    server_type: str - 服务器类型
    players: list - 在线玩家列表
    """
    if server_type == "java":
        server = JavaServer.lookup(server_address)
    elif server_type == "bedrock":
        server = BedrockServer.lookup(server_address)
    else:
        return {"type": "typeError", "data": "服务器类型错误"}
    try:
        # 判断服务器是否开启
        server.ping()

        # 获取服务器所有信息
        status = vars(server.status())["raw"]

        # 判断是否为原版服务器
        flag = True
        for k, v in status.items():
            if k not in ["version", "players", "description", "favicon", "onforcesSecureChat", "previewsChat"]:
                flag = False
            else:
                flag = True
        
        # 获取在线玩家列表
        try:
            players = [i["name"] for i in status["players"]["sample"]]
        except:
            players = []
        
        # 获取服务器图标
        favicon: str | None = status.get("favicon")
        if favicon is not None:
            # 将base64字符串的前缀去除
            favicon = re.sub("^data:image/.+;base64,", "", favicon)
        
        # 获取服务器版本信息
        game_ver = status.get('version').get('name')

        # 获取在线玩家数量
        online_players = status.get('players').get('online')

        # 获取最大玩家数量
        max_players = status.get('players').get('max')

        # 获取服务器Motd
        motd = status.get('description')
        if type(motd) == dict:
            motd = motd.get('text')

    
        # 返回的服务器信息
        server_info = {
            "game_version": game_ver if game_ver is not None else "未知版本",
            "is_vanilla": flag,
            "online_players": online_players if online_players is not None else 0,
            "max_players": max_players if max_players is not None else 0,
            "motd": motd if motd is not None else "未知格式MOTD",
            "favicon": favicon,
            "server_type": server_type,
            "players": players,
            "latency": int(server.ping())
        }
        return {"status": "success", "data": server_info}

    except OSError as e:
        return {"status": "error", "data": "服务器未开启或服务器地址错误"}
    except TimeoutError as e:
        return {"status": "timeout", "data": "访问服务器超时"}
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "data": "出现未知错误"}
    
def base64_to_image(base64_str: str) -> Image:
    """
    将base64字符串转换为PIL Image对象
    :param base64_str: str - base64字符串
    :return: Image - PIL Image对象
    """
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    image = Image.open(BytesIO(base64.b64decode(base64_data)))
    return image

# # print()
# result = ping("otae.cc:2108", "java")
# print("延迟:", result.get("data").get("latency"))
# a.save("favicon.png")