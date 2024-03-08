from typing import Optional
from pathlib import Path
from .utils import ConfigsManager


# 回复消息名称
NICKNAME: str = "otae"

# 数据库（必要）
# 示例："bind": "postgresql://user:password@127.0.0.1:5432/database"
bind: str = "mysql://otae:otae@mcs1-otae.top:3306/db_otaebot"  # 数据库连接链接
bind_a: str = "mysql+aiomysql://otae:otae@mcs1-otae.top:3306/db_otaebot"  # 异步数据库连接链接
sql_name: str = "postgresql"
user: str = "otae"  # 数据用户名
password: str = "otae"  # 数据库密码
address: str = "127.0.0.1"  # 数据库地址
port: str = ""  # 数据库端口
database: str = "db_otaebot"  # 数据库名称

# 代理，例如 "http://127.0.0.1:7890"
SYSTEM_PROXY: Optional[str] = {"https":"https://127.0.0.1:7890","http":"http://127.0.0.1:7890"}  # 全局代理


Config = ConfigsManager(Path() / "configs" / "plugins2config.yaml")
