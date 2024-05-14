# from util import openJson
from pathlib import Path
import json


class Config():
    api_base: str                       # 后端API地址
    use_easy_bg: bool                   # 是否使用简易背景
    compress: bool                      # 是否压缩图片
    bot_name: str                       # bot名称
    bandori_station_token: str          # 车站token
    token_name: str                     # token名称
    api_use_proxy: bool                 # Api是否使用代理
    proxy_url: str                      # 代理地址
    server_list: list                   # 服务器列表

    ban_gacha_simulate_group_data: list  # 禁止抽卡模拟的群
    enable_carNum_prompt_groups: list   # 开启车牌上传提示的群或人

    cmd_list: list                      # 指令列表
    car_config: dict                    # 车牌配置

    def __init__(self):
        if not Path(f"{Path(__file__).parent}/config.json").exists():
            self.api_base = "http://tsugubot.com:8080"
            self.use_easy_bg = True
            self.compress = True
            self.bot_name = "otae"
            self.bandori_station_token = "ZtV4EX2K9Onb"
            self.token_name = "Tsugu"
            self.api_use_proxy = False
            self.proxy_url = "http://tsugubot.com:8080"
            self.server_list = {
                "0": ["日服", "jp"],
                "1": ["国际服", "en"],
                "2": ["台服", "tw"],
                "3": ["国服", "cn"],
                "4": ["韩服", "kr"]
            }
            self.ban_gacha_simulate_group_data = []
            self.enable_carNum_prompt_groups = []
            
            self.cmd_list = [
        {"command_name": ["查插画", "查卡面", "卡面", "km", "ckm"],                         "ifEnable":"True","name":"查询卡面"},
        {"command_name": ["抽卡模拟", "卡池模拟","抽卡"],                                   "ifEnable":"True","name":"抽卡模拟"},
        {"command_name": ["查卡池","查询卡池","ckc","cxkc"],                                "ifEnable":"True","name":"查询卡池"},
        {"command_name": ["查活动", "查询活动", "chd"],                                     "ifEnable":"True","name":"查询活动"},
        {"command_name": ["查歌曲", "查曲","cq","cgq","song"],                              "ifEnable":"True","name":"查询歌曲"},
        {"command_name": ["查询分数表", "查分数表","分数表","fsb","score"],                  "ifEnable":"True","name":"查询歌曲分数表"},
        {"command_name": ["查角色","查询角色","cjs","cxjs"],                                "ifEnable":"True","name":"查询角色"},
        {"command_name": ["查铺面", "查谱面","pm","cpm"],                                   "ifEnable":"True","name":"查询铺面"},
        {"command_name": ["ycxall", "ycx all","全档预测线", "全档预测", "dxall","dx all"],   "ifEnable":"True","name":"全部预测线"},
        {"command_name": ["ycx", "预测线", "dx", "档线", "挡线"],                           "ifEnable":"True","name":"预测线"},
        {"command_name": ["lsycx","历史预测线","lsdx","历史档线","历史挡线"],                "ifEnable":"True","name":"历史预测线"},
        {"command_name": ["ycm", "车来", "有车吗"],                                         "ifEnable":"True","name":"查询车牌"},
        {"command_name": ["查卡","ck"],                                                    "ifEnable":"True","name":"查询卡牌"},
        {"command_name": ["绑定玩家","bdwj","bindplayer"],                                 "ifEnable":"True","name":"绑定玩家"},
        {"command_name": ["解除绑定","解绑玩家","解绑", "jb", "jcbd", "jbwj"],               "ifEnable":"True","name":"解绑玩家"},
        {"command_name": ["验证","绑定验证","验证绑定","yz","bdyz","yzbd"],                  "ifEnable":"True","name":"验证"},
        {"command_name": ["玩家状态","wjzt","playerinfo","info"],                          "ifEnable":"True","name":"玩家信息"},
        {"command_name": ["查玩家","查询玩家","cwj","cxwj","queryplayer"],                  "ifEnable":"True","name":"查询玩家"},
        {"command_name": ["设置主服务器","主服务器","setmainserver","设定主服务器"],          "ifEnable":"True","name":"设置主服务器"},
        {"command_name": ["设置默认服务器","默认服务器","setdefaultserver","设定默认服务器"], "ifEnable":"True","name":"设置默认服务器"},
        {"command_name": ["查询默认数据","查默认","查询服务器","查询设置"],                   "ifEnable":"True","name":"查询默认数据"}
    ]
            
            self.car_config = {
        "car": [
            "车",
            "w",
            "W",
            "国",
            "日",
            "火",
            "q",
            "开",
            "Q",
            "万",
            "缺",
            "来",
            "差",
            "奇迹",
            "冲",
            "途",
            "分",
            "禁"
        ],
        "fake": [
            "114514",
            "假车",
            "测试",
            "野兽",
            "恶臭",
            "1919",
            "下北泽",
            "粪",
            "糞",
            "臭",
            "雀魂",
            "麻将",
            "打牌",
            "maj",
            "麻",
            "[",
            "]",
            "断幺",
            "11451",
            "xiabeize",
            "qq.com",
            "@",
            "q0",
            "q5",
            "q6",
            "q7",
            "q8",
            "q9",
            "q10",
            "腾讯会议",
            "master",
            "疯狂星期四",
            "离开了我们",
            "日元",
            "av",
            "bv"
        ]
    }       
            # 创建并存储配置文件
            self.save()
        
        else:
            configJson = open_json(f"{Path(__file__).parent}/config.json")
            self.api_base = configJson["api_base"]
            self.use_easy_bg = bool(configJson["use_easy_bg"])
            self.compress = bool(configJson["compress"])
            self.bot_name = configJson["bot_name"]
            self.bandori_station_token = configJson["bandori_station_token"]
            self.token_name = configJson["token_name"]
            self.api_use_proxy = bool(configJson["api_use_proxy"])
            self.proxy_url = configJson["proxy_url"]
            self.server_list = configJson["server_list"]
            self.ban_gacha_simulate_group_data = configJson["ban_gacha_simulate_group_data"]
            self.enable_carNum_prompt_groups = configJson["enable_carNum_prompt_groups"]
            self.cmd_list = configJson["cmd_list"]
            self.car_config = configJson["car_config"]

    def save(self):
        data = {
            "api_base": self.api_base,
            "use_easy_bg":self.use_easy_bg,
            "compress": self.compress,
            "bot_name": self.bot_name,
            "bandori_station_token": self.bandori_station_token,
            "token_name": self.token_name,
            "api_use_proxy": self.api_use_proxy,
            "proxy_url": self.proxy_url,
            "server_list": self.server_list,
            "ban_gacha_simulate_group_data": self.ban_gacha_simulate_group_data,
            "enable_carNum_prompt_groups": self.enable_carNum_prompt_groups,
            "cmd_list": self.cmd_list,
            "car_config": self.car_config
        }
        save_json(f"{Path(__file__).parent}/config.json", data)

class User:
    _id: str
    user_id: str
    platform: str
    server_mode: int
    default_server: list[int]
    car: bool
    server_list: list[dict]

    def __init__(
        self,
        _id: str,
        user_id: str,
        platform: str,
        server_mode: int,
        default_server: list[int],
        car: bool,
        server_list: list[dict]
    ):
        """
        Args:
            _id (str): 唯一id
            user_id (str): 用户ID
            platform (str): 平台
            server_mode (int): 服务器模式
            default_server (list[int]): 默认服务器
            car (str): 是否开启车牌转发
            server_list (list[dict]): 服务器列表
        """
        self._id = _id
        self.user_id = user_id
        self.platform = platform
        self.server_mode = server_mode
        self.default_server = default_server
        self.car = car
        self.server_list = server_list

def save_json(path, data) -> bool:
    try:
        with open(path, "w", encoding="UTF-8") as file:
            json.dump(data, file, indent=4,ensure_ascii=False)
        return True
    except Exception as e:
        print(e)
        return False

def open_json(path) -> dict | None:
    try:
        with open(path, "r", encoding="UTF-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(e)
        return None
