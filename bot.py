# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from utils.db import check_db_connection

# Custom your logger
#
# from nonebot.log import logger, default_format

# logger.add("error.log",
#            rotation="00:00",
#            diagnose=False,
#            level="ERROR",
#            format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)


# Please DO NOT modify this file unless you know what you are doing!
# As an alternative, you should use command `nb` or modify `pyproject.toml` to load plugins
nonebot.load_from_toml("pyproject.toml")
nonebot.load_builtin_plugins("echo")
check_db_connection()


if __name__ == "__main__":
    #nonebot.run()
    # nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
