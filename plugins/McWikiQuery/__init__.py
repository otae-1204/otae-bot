from re import I
from lxml import etree

from nonebot import on_regex
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.exception import ActionFailed
from utils.message_builder import image, at
from utils.image_utils import WebImageBuilders
from utils.utils import get_msg_content
from utils.image_utils import BuildImage
from configs.path_config import IMAGE_PATH
import requests
# (^/wiki\ |^/Wiki\ |^/WIKI\ |^/WiKi\ |^查wiki\ |^查Wiki\ |^查WIKI\ |^查WiKi\ )
wiki = on_regex(pattern=r"^/查{0,1}wiki(.+?)$",flags=I)

@wiki.handle()
async def h_r(event: Event):
    msgid = event.get_event_description().split(" ")[1]
    # print("="*50)
    # print(msgid)
    # print("="*50)
    # 获取输入的字符串
    content = "".join(str(event.message).split(" ")[1:])
    try:
        url = requests.get(
            f"https://wiki.biligame.com/mc/index.php?title=特殊:搜索&profile=all&search={content}&fulltext=1")
        src = etree.HTML(url.text).xpath('//a[@data-serp-pos="0"]/@href')
        # print(src)
        if len(src) == 0:
            await wiki.finish("暂时没有你要查找的内容")
        else:
            await wiki.send(Message(f"[CQ:reply,id={msgid}]图片生成中,请稍后"))
            # await wiki.send(Message(f"[CQ:reply,id={msgid}] 111")) 
            web_url = "https://wiki.biligame.com" + src[0]
            print(web_url)
            await WebImageBuilders(fillName="wiki", webUrl=web_url)
            img = BuildImage(h=0, w=0, background=IMAGE_PATH+"/wiki.png")
            while(img.h > 20000):
                img.resize(0.9)
            img.save(IMAGE_PATH+"/wiki.png")
            try:
                await wiki.send(Message(f"[CQ:reply,id={msgid}]")+image("wiki.png"))
            except ActionFailed:
                await wiki.finish("消息可能被风控或出现其他问题,请尝试重新查询")
    except IndexError:
        await wiki.finish("插件出现问题，可尝试联系开发者解决")
