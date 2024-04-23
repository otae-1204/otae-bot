# from util import openJson
from pathlib import Path
import json

class Config:
    api_base: str                       # 后端API地址
    use_easy_bg: bool                   # 是否使用简易背景
    compress: bool                      # 是否压缩图片
    default_servers: list               # 默认服务器
    bot_name: str                       # bot名称
    bandori_station_token: str          # 车站token
    token_name: str                     # token名称
    api_use_proxy: bool                 # Api是否使用代理
    submit_car_number_use_proxy: bool   # 提交车牌号是否使用代理
    proxy_url: str                      # 代理地址
    server_list: list                   # 服务器列表
    
    ban_gacha_simulate_group_data: list # 禁止抽卡模拟的群
    enable_carNum_prompt_groups: list   # 开启车牌上传提示的群或人
    
    cmd_list: list                      # 指令列表
    
    car_config: dict                    # 车牌配置
    
    def __init__(self):
        configJson = openJson(f"{Path(__file__).parent}/config.json")
        self.api_base = configJson["api_base"]
        self.use_easy_bg = bool(configJson["use_easy_bg"])
        self.compress = bool(configJson["compress"])
        self.default_servers = configJson["default_servers"]
        self.bot_name = configJson["bot_name"]
        self.bandori_station_token = configJson["bandori_station_token"]
        self.token_name = configJson["token_name"]
        self.api_use_proxy = bool(configJson["api_use_proxy"])
        self.submit_car_number_use_proxy = bool(configJson["submit_car_number_use_proxy"])
        self.proxy_url = configJson["proxy_url"]
        self.server_list = configJson["server_list"]
        self.ban_gacha_simulate_group_data = configJson["ban_gacha_simulate_group_data"]
        self.enable_carNum_prompt_groups = configJson["enable_carNum_prompt_groups"]
        self.cmd_list = configJson["cmd_list"]
        self.car_config = configJson["car_config"]

def openJson(path) -> dict | None:
    try:
        with open(path, "r", encoding="UTF-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(e)
        return None
