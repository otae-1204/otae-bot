from nonebot import on_command
from utils.message_builder import image
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
import re

Bothelp = on_command("help")

@Bothelp.handle()
async def h_r(event: Event, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        await Bothelp.finish(image("使用说明.png"))
    # 正则表达式读取参数
    elif re.match(r"eft", args.extract_plain_text(),flags=re.I) is not None:
        await Bothelp.finish(image("使用说明-EFT.png"))
    elif re.match(r"bili", args.extract_plain_text(),flags=re.I) is not None:
        await Bothelp.finish(image("使用说明-bili.png"))
    else:
        await Bothelp.finish(image("使用说明.png"))
