import requests
from lxml import etree
from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message

from utils.user_agent import get_user_agent
from utils.utils import get_msg_content

mod = on_command("mod")
item = on_command('资料')


@mod.handle()
async def h_r(event: Event):
    # 获取输入的字符串
    content = get_msg_content(event.get_plaintext()).split(" ")
    name = ""
    # 判断有没有添加查询数量
    try:
        count = int(content[len(content) - 1])
        # 获取要查询的内容
    except ValueError:
        count = 3
        # 获取要查询的内容
    for i in range(0, len(content)):
        name += content[i]
    # 访问mcmod
    url = etree.HTML(requests.get(
        f"https://search.mcmod.cn/s?key={name}", headers=get_user_agent()).text)
    # 爬mod链接链接
    href = url.xpath('//div[@class="head"]/a[@href]/@href')
    # 爬mod标题
    title = url.xpath('//div[@class="head"]')
    # 提取mod标题文本
    for i in range(0, len(title)):
        title[i] = title[i].xpath('.//text()')
    # print(title)
    hrefs = []
    # 获取mod页面链接
    for i in range(0, len(href)):
        ifPrint = href[i].split('/')
        # print(ifPrint)
        if ifPrint[3] == "class":
            hrefs.append(href[i])
    # 判断获取到的结果是否超过3
    if len(hrefs) >= count:
        # 合并标题
        for i in range(0, count):
            for j in range(1, len(title[i])):
                title[i][0] += title[i][j]
        msg = f"Mcmod中符合您搜索的mod如下(仅显示前{count}个)\n"
        # 输出内容
        for i in range(0, count):
            msg += ("{}:\n".format(title[i][0]))
            # print(title[i][0])
            msg += ("{}\n".format(hrefs[i]))
    # 如果不超过3则全部输出
    elif len(hrefs) > 0:
        # 合并内容
        for i in range(0, len(title)):
            for j in range(1, len(title[i])):
                title[i][0] += title[i][j]
                # 输出内容
        msg = "Mcmod中符合您搜索的mod如下\n"
        for i in range(0, len(hrefs)):
            msg += ("{}:\n".format(title[i][0]))
            print(title[i][0])
            msg += ("{}\n".format(hrefs[i]))
    # 如果没找到内容
    else:
        msg = "找不到您搜索的内容，请尝试更换关键词"
    await mod.finish(message=Message(msg))


@item.handle()
async def h_r(event: Event):
    # 获取输入的字符串
    name = get_msg_content(event.get_plaintext()).split(" ")
    url = etree.HTML(
        requests.get(f"https://search.mcmod.cn/s?key={name}&filter=3&mold=0", headers=get_user_agent()).text)
    href = url.xpath('//div[@class="head"]/a[@href]/@href')
    Text = url.xpath('//div[@class="head"]')
    for i in range(0, len(Text)):
        Text[i] = Text[i].xpath('.//text()')
    print(Text)
    if len(href) >= 5:
        for i in range(0, 5):
            for j in range(1, len(Text[i])):
                Text[i][0] += Text[i][j]

        msg = "Mcmod中符合您搜索的资料如下(仅显示前五个)\n"
        for i in range(0, 5):
            msg += ("{}:\n".format(Text[i][0]))
            print(Text[i][0])
            msg += ("{}\n".format(href[i]))
            if i < 4:
                msg += "\n"
    elif len(href) > 0:
        for i in range(0, len(Text)):
            for j in range(1, len(Text[i])):
                Text[i][0] += Text[i][j]

        msg = "Mcmod中符合您搜索的资料如下\n"
        for i in range(0, len(Text)):
            msg += ("{}:\n".format(Text[i][0]))
            print(Text[i][0])
            msg += ("{}\n".format(href[i]))
            if i < (len(Text) - 1):
                msg += "\n"
    else:
        msg = "找不到您搜索的内容，请尝试更换关键词"

    msg = Message(msg)
    await item.finish(msg)
