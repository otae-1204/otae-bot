from nonebot import on_command
from utils.message_builder import image
from nonebot.adapters import Event

Bothelp = on_command("help")

@Bothelp.handle()
async def h_r():
    await Bothelp.finish(image("使用说明.png"))
