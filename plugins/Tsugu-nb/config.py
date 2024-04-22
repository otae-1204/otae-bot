class Config:
    # 后端地址
    backend = "http://tsugubot.com:8080"
    
    # 用户信息后端地址
    user_data_backend = "http://tsugubot.com:8080"
    
    # 后端是否使用代理
    backend_use_proxy = False
    
    # 用户信息后端是否使用代理
    user_data_backend_use_proxy = False
    
    # 提交车牌是否使用代理 
    submit_car_number_use_proxy = False
    
    # 验证玩家绑定是否使用代理
    verify_player_bind_use_proxy = False
    
    # 代理地址
    proxy_url = "http://localhost:7890"
    
    # 用户数据库路径
    user_database_path = None
    
    # Token名称
    token_name = "Tsugu"
    
    # Bandori Station Token
    bandori_station_token = "ZtV4EX2K9Onb"

    # 是否使用简易背景
    use_easy_bg = True
    
    # 是否压缩图片
    compress = True

    # 禁止卡池模拟的群
    ban_gacha_simulate_group_data = []

    # 服务器列表
    server_list = {0: "日服", 1: "国际服", 2: "台服", 3: "国服", 4: "韩服"}
    
    # 服务器名称到索引的映射
    server_name_to_index = {
        "日服": "0",
        "国际服": "1",
        "台服": "2",
        "国服": "3",
        "韩服": "4",
        "jp": "0",
        "en": "1",
        "tw": "2",
        "cn": "3",
        "kr": "4",
    }

    # 服务器索引到名称的映射
    server_index_to_name = {
        "0": "日服",
        "1": "国际服",
        "2": "台服",
        "3": "国服",
        "4": "韩服",
    }

    # 服务器索引到简称的映射
    server_index_to_s_name = {
        "0": "jp",
        "1": "en",
        "2": "tw",
        "3": "cn",
        "4": "kr",
    }

    # 功能开关
    features = {
        # 车牌消息转发
        "car_number_forwarding": True,
        
        # 更换主服务器
        "change_main_server": True,
        
        # 更换卡池服务器
        "switch_car_forwarding": True,
        
        # 绑定玩家
        "bind_player": True,
        
        # 验证玩家绑定
        "change_server_list": True,
        
        # 查询玩家状态
        "player_status": True,
        
        # help
        "help": True,
    }

    # 启用车牌上传提示的群或人数据存放位置
    data_path = "./data.csv"    
    
    # # 启用车牌上传提示的群或人
    # enable_carNum_prompt_groups = []

    # 指令列表
    commands = [
        {"api": "cardIllustration", "command_name": ["/查插画", "/查卡面", "/卡面", "/km"]},
        {"api": "player", "command_name": ["/查玩家", "/查询玩家"]},
        {"api": "gachaSimulate", "command_name": ["/抽卡模拟", "/卡池模拟"]},
        {"api": "gacha", "command_name": ["/查卡池"]},
        {"api": "event", "command_name": ["/查活动", "/查询活动", "/chd"]},
        {"api": "song", "command_name": ["/查歌曲", "/查曲"]},
        {"api": "songMeta", "command_name": ["/查询分数表", "/查分数表"]},
        {"api": "character", "command_name": ["/查角色"]},
        {"api": "chart", "command_name": ["/查铺面", "/查谱面"]},
        {"api": "ycxAll", "command_name": ["/ycxall", "/ycx all","/全档预测线", "/全档预测"]},
        {"api": "ycx", "command_name": ["/ycx", "/预测线"]},
        {"api": "lsycx", "command_name": ["/lsycx","/历史预测线"]},
        {"api": "ycm", "command_name": ["/ycm", "/车来"]},
        {"api": "card", "command_name": ["/查卡","/ck"]},
    ]

    # 车牌配置
    car_config = {
        "car": [
            "q1",
            "q2",
            "q3",
            "q4",
            "Q1",
            "Q2",
            "Q3",
            "Q4",
            "缺1",
            "缺2",
            "缺3",
            "缺4",
            "差1",
            "差2",
            "差3",
            "差4",
            "3火",
            "三火",
            "3把",
            "三把",
            "打满",
            "清火",
            "奇迹",
            "中途",
            "大e",
            "大分e",
            "exi",
            "大分跳",
            "大跳",
            "大a",
            "大s",
            "大分a",
            "大分s",
            "长途",
            "生日车",
            "军训",
            "禁fc",
        ],
        "fake": [
            "114514",
            "野兽",
            "恶臭",
            "1919",
            "下北泽",
            "粪",
            "糞",
            "臭",
            "11451",
            "xiabeize",
            "雀魂",
            "麻将",
            "打牌",
            "maj",
            "麻",
            "[",
            "]",
            "断幺",
            "qq.com",
            "腾讯会议",
            "master",
            "疯狂星期四",
            "离开了我们",
            "日元",
            "av",
            "bv",
        ],
    }
