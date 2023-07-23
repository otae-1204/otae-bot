from logging import Logger
from re import T
from PIL import Image
from flask import redirect
from matplotlib.pyplot import loglog
from nonebot import logger
from src.plugins.HottaHelper.dbUtil import databaseDao
from utils.image_utils import BuildImage
from configs.path_config import IMAGE_PATH


log = Logger("幻塔助手")


def WeaponImg(
    weapons: dict
):
    """
    说明：
    生成一张武器底图
    参数：
        :param weapons: 要生成的武器原字典
    """

    if weapons["grade"] == "RS":
        grade = "R"
    else:
        grade = weapons["grade"]
    try:
        img = BuildImage(w=0, h=0, background=f"{IMAGE_PATH}hotta/weaponsProduct/{weapons['img']}")
    except FileNotFoundError:
        img = BuildImage(w=0, h=0, background=f"{IMAGE_PATH}hotta/{grade}.png")
        wimg = Image.open(f"{IMAGE_PATH}hotta/{weapons['img']}")
        img.paste(img=wimg, pos=(0, 0), alpha=True)
        img.save(f"{IMAGE_PATH}/hotta/weaponsProduct/{weapons['name']}.png")
    return img

# 生成十连武器图片
def TenEvenDrawImg(
    randomWeapons: list,
    userId: str,
    times: float,
    type: str
):
    """
    说明：
    生成一张十连图
    参数：
        :param randomWeapons: 随机抽取的十个武器字典
        :param userId: 交互用户的QQ号
        :param times: 抽卡时时间戳
        :param type: 卡池类型
    """
    extractNumPos = (1154, 109)
    mustgetNumPos = (1858, 109)
    db = databaseDao()
    weapons = []
    for i in range(0, 10):
        weapons.append(WeaponImg(randomWeapons[i]))
    plyaerinfos = db.get_PlayersInfo(userId, type)
    weaponPos = [(185, 315), (567, 315), (949, 315), (1331, 315), (1713, 315),
                 (185, 697), (567, 697), (949, 697), (1331, 697), (1713, 697)]
    bimg = BuildImage(
        w=0, h=0, background=f"{IMAGE_PATH}hotta/十连底图-{type}.png", font_size=80, font="zk.ttf")
    for i in range(0, 10):
        wimg = weapons[i]
        bimg.paste(img=wimg, pos=weaponPos[i], alpha=True)

    if type == "red":
        swimg = BuildImage(
            w=166, h=166, background=f"{IMAGE_PATH}hotta/{db.get_UpWeaponImgUrl()}")
        bimg.paste(img=swimg, pos=(871, 48), alpha=True)
        extractNumPos = (1376, 109)
        mustgetNumPos = (2007, 109)

    bimg.text(pos=extractNumPos, text=str(
        plyaerinfos["extractNum"]), fill=(255, 255, 255))
    bimg.text(pos=mustgetNumPos, text=str(
        plyaerinfos["mustgetNum"]), fill=(255, 255, 255))
    bimg.save(f"{IMAGE_PATH}hotta/TenEvenDraw/TenEvenDraw-{userId}-{times}.png")
    # logger.success("十连图生成成功")
    return "TenEvenDraw-{userId}-{times}.png"

def EvenDrawImg(
    weapons: dict,
    userId: str,
    times: float,
    type: str
):
    """
    说明：
        生成一张抽卡图片
    参数：
        :param weapons: 要生成的武器列表
        :param userId: 交互用户的QQ号
        :param times: 抽卡时时间戳
        :param type: 卡池类型
    """

    # 武器列表排序
    weaponList = []
    temp = []
    weaponsImg = []
    for i in range(0, len(weapons)):
        weaponsImg.append(WeaponImg(weapons[i]))
    for i in range(0, len(weaponsImg)):
        temp.append(weaponsImg[i])
        if (i + 1) % 5 == 0 and i != 0 or i == len(weaponsImg)-1:
            weaponList.append(temp)
            temp = []

    # 生成底板图片
    innerImgW = 86 * 2 + 332 * 5 + 50 * 4
    innerImgH = 86 * 2 + len(weaponList) * 332 + 50 * (len(weaponList)-1)
    innerImg = BuildImage(w=innerImgW+2, h=innerImgH+2,
                          is_alpha=True, color=(204, 204, 204))
    innerImg2 = BuildImage(w=innerImgW, h=innerImgH,
                           is_alpha=True, color=(196, 221, 243))
    innerImg.circle_corner(30)
    innerImg2.circle_corner(30)
    innerImg.paste(img=innerImg2, pos=(1, 1), alpha=True)
    # innerImg.show()
    bgimg = BuildImage(w=innerImgW+99*2, h=innerImgH+99+229, is_alpha=True,
                       background=f"{IMAGE_PATH}hotta/武器列表底图.png", font_size=80, font="zk.ttf")
    bgimg.paste(img=innerImg, pos=(99, 229), alpha=True)
    db = databaseDao()
    # 文字位置
    txtPos = {
        "gold": [(254, 109), (923, 109), (1606, 109)],
        "red": [(96, 109), (599, 109), (1049, 109), (1679, 109)]
    }
    # 文字内容
    txt = {
        "gold": ["卡池类型:", "抽取总数:", "距保底数:"],
        "red": ["卡池类型:", "UP武器:", "抽取总数:", "距保底数:"]
    }
    # 子图片位置
    imgPos = {
        "gold": [(536, 23)],
        "red":  [(378, 23), (871, 48)]
    }
    # 子图片文件
    imgList = {
        "gold": [[f"{IMAGE_PATH}hotta/Gem004.png", 207]],
        "red": [[f"{IMAGE_PATH}hotta/Gem005.png", 207], [f"{IMAGE_PATH}hotta/{db.get_UpWeaponImgUrl()}", 166]]
    }
    # 向图片中添加文字
    for i in range(0, len(txt[type])):
        bgimg.text(pos=txtPos[type][i], text=txt[type]
                          [i], fill=(255, 255, 255))
    # 向图片中添加图片
    for i in range(0, len(imgList[type])):
        bgimg.paste(img=BuildImage(
            w=imgList[type][i][1], h=imgList[type][i][1], background=imgList[type][i][0]), pos=imgPos[type][i], alpha=True)

    # 累计抽取次数以及距保底次数坐标
    extractNumPos = {"gold": (1154, 109), "red": (1376, 109)}
    mustgetNumPos = {"gold": (1858, 109), "red": (2007, 109)}

    plyaerinfos = db.get_PlayersInfo(userId, type)

    # 向图片中添加抽取次数及距保底次数
    bgimg.text(pos=extractNumPos[type], text=str(
        plyaerinfos["extractNum"]), fill=(255, 255, 255))
    bgimg.text(pos=mustgetNumPos[type], text=str(
        plyaerinfos["mustgetNum"]), fill=(255, 255, 255))

    # 武器图片生成&定位
    xPos = 185
    yPos = 315
    for i in range(0, len(weaponList)):
        for j in range(0, len(weaponList[i])):
            wimg = weaponList[i][j]
            bgimg.paste(img=wimg, pos=(xPos, yPos), alpha=True)
            xPos += 50 + 332
        xPos = 185
        yPos += 50 + 332
    bgimg.save(
        f"{IMAGE_PATH}hotta/TenEvenDraw/TenEvenDraw-{userId}-{times}.png")
    logger.success("抽卡图生成成功")

def WeaponListOneImg(
    weapons: dict
):
    bgimg = BuildImage(w=707, h=332, is_alpha=True,
                       font="yuanshen.ttf", font_size=70)
    img = WeaponImg(weapons)
    bgimg.paste(img=img, pos=(0, 0), alpha=True)
    bgimg.text(pos=(360, 0), text="x" +
               str(weapons["count"]), fill=(0, 0, 0), center_type="by_height")
    # bgimg.show()
    return bgimg

# 生成武器列表图


def WeaponListImg(
    weapons: list,
    userId: str,
    type: str
):
    """
        说明:
            生成指定用户的抽取列表图
        参数:
            :param weapons: 武器列表
            :param userId: 用户QQ号
            :param type: 池子类型
    """
    width = 2391  # 图片宽度
    height = 606  # 图片高度
    if len(weapons) == 0:
        bgimg = BuildImage(w=width, h=height,
                           background=IMAGE_PATH+"hotta/武器列表底图.png", font_size=75, font="yuanshen.ttf")
        bgimg1 = BuildImage(w=width-82, h=height-82,
                            is_alpha=True, color="#c4ddf3")
        bgimg1.circle_corner(20)
        bgimg.text(text="没有抽卡数据", pos=(0, 0), fill=(
            0, 0, 0), center_type="center")
        bgimg.save(f"{IMAGE_PATH}hotta/extractList/{userId}.png")
        return
    db = databaseDao()
    plyaerinfos = db.get_PlayersInfo(userId, type)
    print(plyaerinfos)
    weaponList = []
    temp = []
    weaponsImg = []
    for i in range(0, len(weapons)):
        weaponsImg.append(WeaponListOneImg(weapons[i]))

    for i in range(0, len(weaponsImg)):
        temp.append(weaponsImg[i])
        if (i + 1) % 3 == 0 and i != 0 or i == len(weaponsImg)-1:
            weaponList.append(temp)
            temp = []

    # [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
    if len(weaponList[0]) < 3:  # 如果武器数量小于3
        # 图片宽 = 边框距离*2 + 每个武器间隔 + 47
        width = 41*2 + 754*(len(weaponList[0])) + 47
    if len(weaponList) > 1:  # 如果行数大于1
        # 图片高 = 原图片高度 + (单个武器图片高度 + 每个武器间距)*(行数-1)
        height = 606 + (379*(len(weaponList)-1))
    bgimg = BuildImage(w=width, h=height,
                       background=IMAGE_PATH+"hotta/武器列表底图.png", font_size=65, font="zk.ttf")
    bgimg1 = BuildImage(w=width-82, h=height-82,
                        is_alpha=True, color="#c4ddf3")
    bgimg1.circle_corner(20)
    bgimg.paste(img=bgimg1, pos=(41, 41), alpha=True)
    bgimg.text(pos=(82, 82), text="已抽取次数:" +
               str(plyaerinfos["extractNum"]), fill=(0, 0, 0))
    xPos = 88
    yPos = 186

    for i in weaponList:
        for j in i:
            bgimg.paste(img=j, pos=(xPos, yPos), alpha=True)
            xPos += 754
        xPos = 88
        yPos += 379
    bgimg.save(f"{IMAGE_PATH}hotta/extractList/{userId}.png")
