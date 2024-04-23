from util import *
from entity import Config
import time

config = Config()


async def CardIllustration(cardId: int) -> dict:
    """
    说明:
        获取卡片插画
    参数:
        cardId: 卡片ID
    返回:
        dict: ["base64","xxxxxxxxxxx"]
    """
    url = f"{config.api_base}/getCardIllustration"
    data = {
        "cardId": cardId
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def gachaSimulate(
    server_mode: int,
    gachaId: int = None
):
    """
    说明:
        模拟抽卡
    参数:
        server_mode: 服务器模式     0-4
        gachaId:     卡池ID        int        
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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

async def searchGacha(
    default_servers: int,
    gachaId: int,
):
    """
    说明:
        查询卡池
    参数:
        default_servers: 默认服务器       list
        gachaId:         卡池ID           int
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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

async def searchEvent(
    default_servers: int,
    eventName: str,
):
    """
    说明:
        查询活动
    参数:
        default_servers: 默认服务器        list
        eventId:         活动ID           int
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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

async def searchSong(
    default_servers: int,
    songName: str,
):
    """
    说明:
        查询歌曲
    参数:
        default_servers: 默认服务器        list
        songName:        歌曲名称
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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

async def songMeta(
    default_servers: int,
    server: int,
):
    """
    说明:
        查询歌曲Meta
    参数:
        default_servers: 默认服务器        list
        server:          服务器id          0-4
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

async def searchCharacter(
    default_servers: int,
    characterName: str,
):
    """
    说明:
        查询角色
    参数:
        default_servers: 默认服务器      list
        characterName:   角色名称
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

async def songChart(
    default_servers: int,
    songName: int,
    difficulty: int,
):
    """
    说明:
        查询歌曲谱面
    参数:
        default_servers: 默认服务器     list
        songId:          歌曲id        int
        difficultyText:  难度          easy,normal,hard,expert,special
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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

async def ycxAll(
    server: int,
    eventId: int = None
):
    """
    说明:
        查询全服排行
    参数:
        server: 服务器id
        eventId: 活动id
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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
        查询排行
    参数:
        server:  服务器id  0-3
        tier:    排名      int
        eventId: 活动id    int
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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
        查询历史排行
    参数:
        server:  服务器id  0-3
        tier:    排名      int
        eventId: 活动id    int
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

async def roomList(
    roomList: list
):
    """
    说明:
        车牌绘图
    参数:
        roomList: 车牌列表 list
    返回:
        dict: ["status": "suc", "data": [xxxxx]]
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
        dict: ["base64","xxxxxxxxxxx"]
    """
    url = f"{config.api_base}/station/queryAllRoom"
    result = await a_get_data_from_backend_get(url)
    if result["status"] == "success":
        return await roomList(result["data"])
    else:
        return [{"type": "string", "string": "查询失败"}]

async def submitRoomNumber(
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
        number:              车牌号
        rawMessage:          原始消息
        platform:            平台
        user_id:             用户id
        userName:            用户名
        bandoriStationToken: token
    返回:
        dict: ["base64","xxxxxxxxxxx"]
    """
    url = f"{config.api_base}/station/submitRoomNumber"
    data = {
        "number": number,
        "rawMessage": rawMessage,
        "platform": platform,
        "user_id": user_id,
        "userName": userName,
        "time": int(time.time())
        # "bandoriStationToken": config.bandori_station_token
    }
    result = await a_get_data_from_backend(url, data)
    return result

async def searchCard(
    default_servers: int,
    cardName: str,
):
    """
    说明:
        查询卡片
    参数:
        default_servers: 默认服务器      list
        cardName:        卡片名称        str
    返回:
        dict: ["base64","xxxxxxxxxxx"]
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








