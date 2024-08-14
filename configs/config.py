from typing import Optional
from pathlib import Path
from .utils import ConfigsManager
import os, json


# 回复消息名称
NICKNAME: str = "otae"

# 数据库（必要）
# 示例："bind": "postgresql://user:password@127.0.0.1:5432/database"
bind: str = "mysql://otae:otae@127.0.0.1:3306/db_otaebot"  # 数据库连接链接
bind_a: str = "mysql+aiomysql://otae:otae@127.0.0.1:3306/db_otaebot"  # 异步数据库连接链接
sql_name: str = "postgresql"
user: str = "otae"  # 数据用户名
password: str = "otae"  # 数据库密码
address: str = "127.0.0.1"  # 数据库地址
port: str = ""  # 数据库端口
database: str = "db_otaebot"  # 数据库名称

# 代理，例如 "http://127.0.0.1:7890"
SYSTEM_PROXY: Optional[str] = {"https":"https://127.0.0.1:7890","http":"http://127.0.0.1:7890"}  # 全局代理


Config = ConfigsManager(Path() / "configs" / "plugins2config.yaml")

class DateBase_Config():
    """
        数据库配置
    """
    # 数据库连接链接
    bind: str = "mongodb://"
    # 异步数据库连接链接
    bind_a: str = "mongodb://"
    # 数据库类型
    sql_name: str = "mongodb"
    # 数据用户名
    user: str = "otae"
    # 数据库密码
    password: str = "otae"
    # 数据库地址
    address: str = "127.0.0.1"
    # 数据库端口
    port: str = ""
    # 数据库名称
    database: str = "db_otaebot"


class Plugin_Config():
    """
        插件配置
    """
    # 插件名称
    plugin_name: str
    # 插件配置位置
    plugin_config_path: Path
    # 插件配置内容
    plugin_content: dict
    
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.plugin_config_path = Path("configs") / f"{plugin_name}/config.json" 
        self.plugin_content = openJson(self.plugin_config_path)
    
    def update(self):
        saveJson(self.plugin_config_path, self.plugin_content)

    
# 代理，例如 "http://127.0.0.1:7890"
SYSTEM_PROXY: Optional[str] = {"https":"https://127.0.0.1:7890","http":"http://127.0.0.1:7890"}  # 全局代理

def openJson(json_filename:str):
    # 检查文件夹是否存在
    if not os.path.exists(json_filename.parent):
        os.makedirs(json_filename.parent)
    if not os.path.exists(json_filename):
        with open(json_filename, 'w') as f:
            f.write("{}")
            f.close()
    with open(json_filename, 'r') as f:
        data = json.load(f)
    return data

def saveJson(json_filename:str,data:dict):
    with open(json_filename, 'w') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)