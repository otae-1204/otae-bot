from lxml import etree
from nonebot import on_regex
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.exception import ActionFailed
from utils.message_builder import image, at
from utils.image_utils import WebImageBuilders
from utils.utils import get_msg_content
import requests


wiki = on_regex(pattern="(^/trwiki\ |^/TrWiki\ |^/TRWIKI\ |^/TrWiKi\ |^查Tr\ |^查TR\ |^查tr\ )")


@wiki.handle()
async def h_r(event:Event):
    # 获取输入的字符串
    content = get_msg_content(event.get_plaintext())

    try:
        url = requests.get(
            f"https://searchwiki.biligame.com/tr/index.php?search={content}&title=特殊%3A搜索&profile=default&fulltext=1")
        src = etree.HTML(url.text).xpath('//a[@data-serp-pos="0"]/@href')
        if len(src) == 0:
            await wiki.finish(Message("暂时没有你要查找的内容"))
        else:
            await wiki.send(at(event.get_user_id()) + "图片生成中,请稍后")
            web_url = "https://wiki.biligame.com" + src[0]
            WebImageBuilders(fillName="tr_wiki", webUrl=web_url)
            try:
                await wiki.send(image("tr_wiki.png"))
            except ActionFailed:
                await wiki.finish("消息可能被风控或出现其他问题,请尝试重新查询")
    except IndexError:
        await wiki.finish(Message("插件出现问题，请联系开发者解决"))
