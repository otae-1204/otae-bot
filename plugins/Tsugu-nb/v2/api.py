from util import *
from entity import Config
import time

config = Config()


async def card_illustration(cardId: int) -> dict:
    """
    说明:
        获取卡片插画
    参数:
        cardId: 卡片ID 如:947
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/getCardIllustration"
    data = {
        "cardId": cardId
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def gacha_simulate(
    server_mode: int | str,
    gachaId: int = None
):
    """
    说明:
        模拟抽卡
    参数:
        server_mode: 服务器id  例: 4 范围: 0-4
        gachaId:     卡池ID    例: 228       
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/gachaSimulate"
    data = {
        "server_mode": server_mode,
        "compress": config.compress
    }
    if gachaId:
        data["gachaId"] = gachaId
    result = await a_get_data_from_backend(url, data)
    return result

async def search_gacha(
    default_servers: list[int],
    gachaId: int,
):
    """
    说明:
        查询卡池
    参数:
        default_servers: 默认服务器编号[主,副]  如: [3,0]  范围: 0-4
        gachaId:         卡池ID                如: 228
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/searchGacha"
    data = {
        "default_servers": default_servers,
        "gachaId": gachaId,
        "useEasyBG": config.use_easy_bg,
        "compress": config.compress
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def search_event(
    default_servers: list[int],
    eventName: str,
):
    """
    说明:
        查询活动
    参数:
        default_servers: 默认服务器编号[主,副]  如: [3,0]  范围: 0-4
        eventId:         活动id或名称          如: 41/双重彩虹
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/searchEvent"
    data = {
        "default_servers": default_servers,
        "text": eventName,
        "useEasyBG": config.use_easy_bg,
        "compress": config.compress
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def search_song(
    default_servers: list[int],
    songName: str,
):
    """
    说明:
        查询歌曲
    参数:
        default_servers: 默认服务器编号[主,副]  如: [3,0]  范围: 0-4
        songName:        歌曲名称              如: Jumpin
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/searchSong"
    data = {
        "default_servers": default_servers,
        "text": songName,
        "useEasyBG": config.use_easy_bg,
        "compress": config.compress
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def song_meta(
    default_servers: list[int],
    server: int,
):
    """
    说明:
        查询歌曲Meta
    参数:
        default_servers: 默认服务器编号[主,副]  如: [3,0]  范围: 0-4
        server:          服务器id              如: 3      范围: 0-4
    返回:
        dict: ["base64","xxxxxxxxxxx"]
    """
    url = f"{config.api_base}/songMeta"
    data = {
        "default_servers": default_servers,
        "server": server,
        "compress": config.compress
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def search_character(
    default_servers: list[int],
    characterName: str,
):
    """
    说明:
        查询角色
    参数:
        default_servers: 默认服务器编号[主,副]  如: [3,0]  范围: 0-4
        characterName:   角色名称              如: otae
    返回:
        dict: ["base64","xxxxxxxxxxx"]
    """
    url = f"{config.api_base}/searchCharacter"
    data = {
        "default_servers": default_servers,
        "text": characterName,
        "compress": config.compress
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def song_chart(
    default_servers: list[int],
    songName: int,
    difficulty: int,
):
    """
    说明:
        查询歌曲谱面
    参数:
        default_servers: 默认服务器编号[主,副]  如: [3,0]  范围: 0-4
        songId:          歌曲id                如: 170
        difficultyText:  难度                  如: expert 范围: easy/normal/hard/expert/special
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/songChart"
    data = {
        "default_servers": default_servers,
        "songId": songName,
        "difficultyText": difficulty,
        "compress": config.compress
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def ycx_all(
    server: int,
    eventId: int = None
):
    """
    说明:
        查询全档位预测线
    参数:
        server: 服务器id  如: 3  范围: 0-4
        eventId: 活动id   如: 41
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/ycxAll"
    data = {
        "server": server,
        "compress": config.compress
    }
    if eventId:
        data["eventId"] = eventId
    result = await a_get_data_from_backend(url, data)
    return result

async def ycx(
    server: int,
    tier: int,
    eventId: int = None
):
    """
    说明:
        查询排行榜预测线
    参数:
        server:  服务器id  如: 3     范围: 0-4
        tier:    排名      如: 100   范围: 10,20,30,50,100,200,300,500,1000,......
        eventId: 活动id    如: 41
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/ycx"
    data = {
        "server": server,
        "tier": tier,
        "compress": config.compress
    }
    if eventId:
        data["eventId"] = eventId
    result = await a_get_data_from_backend(url, data)
    return result

async def lsycx(
        server: int,
        tier: int,
        eventId: int = None
    ):
    """
    说明:
        查询历史排行榜分数线
    参数:
        server:  服务器id  如: 3     范围: 0-4
        tier:    排名      如: 100   范围: 10,20,30,50,100,200,300,500,1000,......
        eventId: 活动id    如: 41
    返回:
        dict: ["base64","xxxxxxxxxxx"]
    """
    url = f"{config.api_base}/lsycx"
    data = {
        "server": server,
        "tier": tier,
        "compress": config.compress
    }
    if eventId:
        data["eventId"] = eventId
    result = await a_get_data_from_backend(url, data)
    return result

async def room_list(
    roomList: list
):
    """
    说明:
        车牌绘图
    参数:
        roomList: 车牌列表 
        如: [{"number": 234211,"rawMessage": "234211 测试q1","source": "BandoriStation","userId": xxx,"time": xxx,"avanter": "","userName": ""}]
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/roomList"
    data = {
        "roomList": roomList,
        "compress": config.compress
    }
    print(data)
    result = await a_get_data_from_backend(url, data)
    print(result)
    return result

async def ycm():
    """
    说明:
        查询最近车站车牌
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/station/queryAllRoom"
    result = await a_get_data_from_backend_get(url)
    if result["status"] == "success":
        return await room_list(result["data"])
    else:
        return [{"type": "string", "string": "查询失败"}]

async def submit_room_number(
    number: int,
    rawMessage: str,
    platform: str,
    user_id: str,
    userName: str
):
    """
    说明:
        提交车牌号
    参数:
        number:       车牌号    如: 125231
        rawMessage:   原始消息  如: 125231 测试q1
        platform:     平台      如: onebot
        user_id:      用户id    如: 2461673400
        userName:     用户名    如: otae
    返回:
        dict: {"status": "suc", "data": [xxxxx]}
    """
    url = f"{config.api_base}/station/submitRoomNumber"
    data = {
        "number": number,
        "rawMessage": rawMessage,
        "platform": platform,
        "user_id": user_id,
        "userName": userName,
        "time": int(time.time()),
        "bandoriStationToken": config.bandori_station_token
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def search_card(
    default_servers: list[int],
    cardName: str,
):
    """
    说明:
        查询卡片
    参数:
        default_servers: 默认服务器编号[主,副]  如: [3,0]  范围: 0-4
        cardName:        卡片编号/名称         如: 947/otae 
    返回:
        list[dict]: [{"type": "base64/string", "string": "xxxxx"}]
    """
    url = f"{config.api_base}/searchCard"
    data = {
        "default_servers": default_servers,
        "text": cardName,
        "useEasyBG": config.use_easy_bg,
        "compress": config.compress
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def get_user_data(
    platform: str,
    user_id: str
):
    """
    :
        获取用户数据
    参数:
        platform: 平台    如: onebot
        user_id:  用户id  如: 2461673400
    返回:
        list[dict]: [{"status": "success", "data": {"_id": "xxx",......}}]
    """
    url = f"{config.api_base}/user/getUserData"
    data = {
        "platform": platform,
        "user_id": user_id
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def bind_player_request(
    platform: str,
    user_id: str,
    bindType: bool,
    server: int = 3
):
    """
    说明:
        绑定玩家ID
    参数:
        platform: 平台     如: onebot
        user_id:  用户id   如: 2461673400
        bindType: 绑定类型  如: True       范围: True/False
        server:   服务器id  如: 3          范围: 0-4 默认3既国服    
    返回:
        dict: {"status": "success","data": {"verifyCode": xxxxx}}
    """
    url = f"{config.api_base}/user/bindPlayerRequest"
    data = {
        "platform": platform,
        "user_id": user_id,
        "server": server,
        "bindType": bindType
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def bind_player_verification(
    platform: str,
    user_id: str,
    playerId: int,
    bindType: bool,
    server: str = 3
):
    """
    说明:
        绑定玩家ID
    参数:
        platform: 平台      如: onebot
        user_id:  用户id    如: 2461673400
        playerId: 玩家id    如: 1002545123
        bindType: 绑定类型  如: True       范围: True/False
        server:   服务器    如: 3          范围: 0-4 默认3既国服
    返回:
        dict: {'status': 'success', 'data': '绑定玩家1002545123成功'}
    """
    url = f"{config.api_base}/user/bindPlayerVerification"
    data = {
        "platform": platform,
        "user_id": user_id,
        "server": server,
        "playerId": playerId,
        "bindType": bindType
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def set_server_mode(
    platform: str,
    user_id: str,
    text: str
):
    """
    说明:
        设置服务器模式
    参数:
        platform: 平台      如: onebot
        user_id:  用户id    如: 2461673400
        text:     服务器    如: jp/3        范围: [cn,jp]/0-4
    返回:
        dict: {'status': 'success'}
    """
    url = f"{config.api_base}/user/changeUserData/setServerMode"
    data = {
        "platform": platform,
        "user_id": user_id,
        "text": text
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def set_car_forwarding(
    platform: str,
    user_id: str,
    status: bool
):
    """
    说明:
        设置玩家车牌转发
    参数:
        platform: 平台      如: onebot
        user_id:  用户id    如: 2461673400
        status:   状态      如: True       范围: True/False    
    """
    url = f"{config.api_base}/user/changeUserData/setCarForwarding"
    data = {
        "platform": platform,
        "user_id": user_id,
        "status": status
    }
    result = await a_get_data_from_backend(url, data)
    return result
