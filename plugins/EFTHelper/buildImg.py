import os
import requests

from configs.config import SYSTEM_PROXY
from configs.path_config import IMAGE_PATH
from plugins.EFTHelper.db import query_task_name
from plugins.EFTHelper.object import AmmoMoreInfo
from utils.image_utils import BuildImage
from utils.user_agent import get_user_agent

path = IMAGE_PATH + 'EFTHelper/'


# 子弹简略信息图片绘制
def build_ammo_image(ammo, qqId) -> int:
    # 判断是否有数据
    try:
        if len(ammo) == 0:
            return 0
    except Exception as e:
        print("粗略图绘制失败")
        print(e)
        return -1

    # 主体绘制
    try:
        # 行数
        rowN = 15 if len(ammo) > 15 else len(ammo)

        # 列高 = 顶内高 + (行数 * 行高) + (行数 - 1) * 行间隔 + 底内高
        ch = 150 + (rowN * 425) + (rowN - 1) * 65 + 100

        # 列宽 = 左内宽 + 行长 + 右内宽 338+25 = 363
        cw = 80 + 1530 + 80

        # 背景高度 = 顶外高 + 列高 + 底外高
        bgh = 600 + ch + 150

        # 列数 341
        colN = int(
            len(ammo) / 15) if len(ammo) % 15 == 0 else int(len(ammo) / 15) + 1

        # 背景宽度 = 左外宽 + (列宽 * 列数) + (列数 - 1) * 列间隔 + 右外宽
        bgw = 150 + (cw * colN) + (colN - 1) * 125 + 150

        # 创建背景
        bg = BuildImage(w=bgw, h=bgh)
        bg1 = BuildImage(w=0, h=0, background=path + 'UI/bg.png')

        # 创建长条
        strip = BuildImage(w=0, h=0, background=path + 'UI/长条.png')

        # 拼接背景
        xn = 0 if bg.w <= 792 else int(bg.w / 792)
        yn = 0 if bg.h <= 792 else int(bg.h / 792)
        for i in range(0, xn + 1):
            for j in range(0, yn + 1):
                bg.paste(bg1, (i * 792, j * 792))
                # bg.show()
        print("=-=" * 20)
        print("背景绘制完毕")
        print("=-=" * 20)

        # 按照15个一列将列表分割
        ammoList = [ammo[i:i + 15] for i in range(0, len(ammo), 15)]

        # 拼接标题
        bg.paste(pos=(100, 150), img=BuildImage(
            w=0, h=0, background=path + "UI/查询子弹子标题.png"), alpha=True)

        # 创建列
        for i in range(0, colN):
            rowN = len(ammoList[i])
            ch = 150 + (rowN * 425) + (rowN - 1) * 65 + 100

            # 创建列背景
            col = BuildImage(w=cw, h=ch, color=(161, 198, 234))
            col.circle_corner(50)
            col_bg1 = BuildImage(w=cw - 20, h=ch - 20, color=(218, 227, 229))
            col_bg1.circle_corner(50)

            # 拼接列背景
            col.paste(col_bg1, (10, 10), alpha=True)

            # 创建行
            for j in range(0, len(ammoList[i])):
                # 创建行背景
                row = BuildImage(w=1530, h=425, is_alpha=True,
                                 font="default.ttf", font_size=75)
                print("行背景创建完毕")

                # 拼接长条
                row.paste(strip, (0, 415))
                print("行长条粘贴完毕")

                # 创建并粘贴子弹图片
                bulletImg = BuildImage(
                    w=320, h=320, is_alpha=True, background=path + f"bullet/{ammoList[i][j].img}")
                row.paste(bulletImg, (30, 0))
                print("子弹图片粘贴完毕")

                # 创建并粘贴子弹信息
                idTxt = BuildImage(w=0, h=0, font="default.ttf", font_size=65, font_color=(
                    130, 149, 153), plain_text="id:" + str(ammoList[i][j].id), is_alpha=True)
                row.paste(idTxt, (50, 315), alpha=True)
                row.text(pos=(405, -10), text="名称 " +
                                              ammoList[i][j].name, fill=(80,80,80))
                row.text(pos=(405, 85), text="口径 " +
                                             ammoList[i][j].caliber, fill=(80,80,80))
                row.text(pos=(405, 180), text="肉伤 " + (((str(ammoList[i][j].projectileCount) + "x")
                                                        if ammoList[i][j].projectileCount != 1 else "") + str(
                    ammoList[i][j].damage)), fill=(80,80,80))
                row.text(pos=(405, 275), text="穿甲 " +
                                              str(ammoList[i][j].penetrationPower), fill=(80,80,80))
                accuracyModifier = round(
                    ammoList[i][j].accuracyModifier * 100, 1)
                print("子弹基础信息绘制完毕")

                # 精度修正颜色
                if accuracyModifier > 0:
                    color = (0, 255, 0)
                elif accuracyModifier < 0:
                    color = (255, 0, 0)
                else:
                    color = (80,80,80)
                row.text(pos=(825, 180), text="精度", fill=(80,80,80))
                row.text(pos=(1010, 180), text=("+" + str(accuracyModifier) + "%" if accuracyModifier > 0 else
                                                str(accuracyModifier) + "%"), fill=color)
                recoilModifier = round(ammoList[i][j].recoilModifier * 100, 1)
                print("子弹精度绘制完毕")

                # 后座力修正颜色
                if recoilModifier > 0:
                    color = (255, 0, 0)
                elif recoilModifier < 0:
                    color = (0, 255, 0)
                else:
                    color = (80,80,80)
                row.text(pos=(825, 275), text="后座", fill=(80,80,80))
                row.text(pos=(1010, 275), text=("+" + str(recoilModifier) + "%" if recoilModifier > 0 else
                                                str(recoilModifier) + "%"), fill=color)
                row.text(pos=(
                    1380, 180), text="禁售" if ammoList[i][j].marketSale == 0 else " ", fill=(255, 0, 0))
                color = (0, 0, 0)
                print("子弹后座以及禁售绘制完毕")

                # 弹迹颜色
                if ammoList[i][j].tracerColor == "red" or ammoList[i][j].tracerColor == "tracerRed":
                    color = (255, 0, 0)
                elif ammoList[i][j].tracerColor == "green" or ammoList[i][j].tracerColor == "tracerGreen":
                    color = (0, 255, 0)
                elif ammoList[i][j].tracerColor == "yellow":
                    color = (255, 255, 0)
                row.text(
                    pos=(1325, 275), text="曳" if ammoList[i][j].tracer else " ", fill=color)
                row.text(pos=(
                    1425, 275), text="亚" if ammoList[i][j].initialSpeed <= 340 else " ", fill=(80,80,80))
                print("子弹弹迹绘制完毕")

                # 粘贴行
                col.paste(row, (80, 150 + j * 490), alpha=True)

            # 粘贴列
            bg.paste(col, (150 + i * 1815, 600), alpha=True)
            print("=-=" * 20)
            print(f"列{i + 1}绘制完毕")
            print("=-=" * 20)

        # 保存图片
        bg.save(path + f"img/{qqId}.png")
        print("=-=" * 20)
        print("子弹粗略图生成完毕")
        print("=-=" * 20)
        return 1
    except Exception as e:
        print("粗略图图片绘制失败")
        print(e)
        return -1


# 子弹详细信息图片绘制
async def build_ammo_info(ammoInfo, ammoMoreInfo: AmmoMoreInfo, qqId) -> int:
    if ammoInfo is not None:
        # 获取画布宽度 30 + 30 + 340
        bgw = 3930

        # 获取画布高度 顶外高 + 列高(280 + 30 + 商人获取渠道数*110 + 工作台获取渠道数*135) + 底外高
        bgh = 1200 + 2400 + 200 + len(ammoMoreInfo.buyFor) * 850 + len(ammoMoreInfo.craftsFor) * 1350 + 350 + 300

        # 创建画布
        bg = BuildImage(w=bgw, h=bgh, color=(55, 55, 55), font="default.ttf", font_size=150)

        # 填充背景图片
        bg1 = BuildImage(w=0, h=0, background=path + 'UI/bg.png')
        xn = 0 if bg.w <= 792 else int(bg.w / 792)
        yn = 0 if bg.h <= 792 else int(bg.h / 792)
        for i in range(0, xn + 1):
            for j in range(0, yn + 1):
                bg.paste(bg1, (i * 792, j * 792))

        # 绘制标题
        bg.paste(pos=(200, 300), img=BuildImage(w=0, h=0, background=path + "UI/查询子弹子标题-详细.png"), alpha=True)

        # 绘制信息背景外部
        infoBg = BuildImage(w=bgw - 600, h=bgh - 1500, color=(161, 198, 234))

        # 绘制信息背景外部圆角
        infoBg.circle_corner(100)

        # 绘制信息背景内部
        infoBg1 = BuildImage(w=bgw - 640, h=bgh - 1540, color=(218, 227, 229))

        # 绘制信息背景内部圆角
        infoBg1.circle_corner(100)

        # 拼接信息背景
        infoBg.paste(infoBg1, (20, 20), alpha=True)

        # 绘制信息背景
        bg.paste(infoBg, (300, 1200), alpha=True)

        # 绘制子弹文字
        title = BuildImage(w=0, h=0, font="default.ttf", font_size=200, plain_text="子弹数据", is_alpha=True,
                           font_color=(55, 55, 55))
        bg.paste(title, (480, 1350), alpha=True)

        # 绘制长条分割线
        line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
        bg.paste(pos=(430, 1650), img=line, alpha=True)

        # 绘制子弹图片
        img = BuildImage(w=640, h=640, background=path + f"bullet/{ammoInfo.img}")
        img.circle_corner(60)
        bg.paste(pos=(550, 1830), img=img, alpha=True)

        # 绘制子弹名称
        name = BuildImage(w=0, h=0, font="default.ttf", font_size=120, plain_text="名称 " + ammoInfo.name, is_alpha=True,
                          font_color=(55, 55, 55))
        bg.paste(name, (1330, 1860), alpha=True)

        # 绘制子弹口径
        caliber = BuildImage(w=0, h=0, font="default.ttf", font_size=120, plain_text="口径 " + ammoInfo.caliber,
                             is_alpha=True, font_color=(55, 55, 55))
        bg.paste(caliber, (1330, 2070), alpha=True)

        # 绘制子弹类型
        typeName = ""
        totalDamage = ammoInfo.damage * ammoInfo.projectileCount
        typeName += "肉伤弹 " if int(totalDamage) > 75 and ammoInfo.penetrationPower < 20 else ""
        typeName += "高级穿甲弹 " if 50 <= ammoInfo.penetrationPower < 60 else ""
        typeName += "顶级穿甲弹 " if ammoInfo.penetrationPower >= 60 else ""
        typeName += "亚音速弹" if ammoInfo.initialSpeed < 340 else ""
        typeImg = BuildImage(w=0, h=0, font="default.ttf", font_size=120, plain_text="类型 " + typeName, is_alpha=True,
                             font_color=(55, 55, 55))
        bg.paste(typeImg, (1330, 2280), alpha=True)

        # 绘制子弹id
        id = BuildImage(w=0, h=0, font="default.ttf", font_size=100, plain_text="id: " + str(ammoInfo.id),
                        is_alpha=True, font_color=(60, 60, 60))
        bg.paste(id, (600, 2470), alpha=True)

        damageNum = ammoInfo.damage if ammoInfo.projectileCount == 1 else str(ammoInfo.damage) + "x" + str(
            ammoInfo.projectileCount)
        # 绘制子弹肉伤
        damage = BuildImage(w=0, h=0, font="default.ttf", font_size=120, plain_text="子弹肉伤 " + str(damageNum),
                            is_alpha=True, font_color=(55, 55, 55))
        bg.paste(damage, (470, 2700), alpha=True)

        # 绘制子弹穿甲
        penetrationPower = BuildImage(w=0, h=0, font="default.ttf", font_size=120,
                                      plain_text="子弹穿甲 " + str(ammoInfo.penetrationPower), is_alpha=True,
                                      font_color=(55, 55, 55))
        bg.paste(penetrationPower, (470, 2900), alpha=True)

        # 绘制子弹最大堆叠
        stackMaxSize = BuildImage(w=0, h=0, font="default.ttf", font_size=120,
                                  plain_text="最大堆叠 " + str(ammoInfo.stackMaxSize), is_alpha=True,
                                  font_color=(55, 55, 55))
        bg.paste(stackMaxSize, (470, 3100), alpha=True)

        # 绘制曳光颜色
        colorName = "无"
        if ammoInfo.tracer:
            if ammoInfo.tracerColor == "red" or ammoInfo.tracerColor == "tracerRed":
                colorName = "红"
            elif ammoInfo.tracerColor == "green" or ammoInfo.tracerColor == "tracerGreen":
                colorName = "绿"
            elif ammoInfo.tracerColor == "yellow":
                colorName = "黄"
        tracerColor = BuildImage(w=0, h=0, font="default.ttf", font_size=120, plain_text="曳光颜色 " + colorName,
                                 is_alpha=True, font_color=(55, 55, 55))
        bg.paste(tracerColor, (470, 3300), alpha=True)

        # 绘制小出血修正
        lightBleedModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=120,
                                        plain_text=f"小出血修正 {int(ammoInfo.lightBleedModifier * 100)}%",
                                        is_alpha=True, font_color=(55, 55, 55))
        bg.paste(lightBleedModifier, (1450, 2700), alpha=True)

        # 绘制大出血修正
        heavyBleedModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=120,
                                        plain_text=f"大出血修正 {int(ammoInfo.heavyBleedModifier * 100)}%",
                                        is_alpha=True, font_color=(55, 55, 55))
        bg.paste(heavyBleedModifier, (1450, 2900), alpha=True)

        # 绘制受伤掉耐
        staminaBurnPerDamage = BuildImage(w=0, h=0, font="default.ttf", font_size=120,
                                          plain_text=f"被击打掉耐 {int(ammoInfo.staminaBurnPerDamage * 100)}%",
                                          is_alpha=True, font_color=(55, 55, 55))
        bg.paste(staminaBurnPerDamage, (1450, 3100), alpha=True)

        # 绘制护甲损伤
        armorDamage = BuildImage(w=0, h=0, font="default.ttf", font_size=120,
                                 plain_text=f"对护甲损伤 {int(ammoInfo.armorDamage)}%",
                                 is_alpha=True, font_color=(55, 55, 55))
        bg.paste(armorDamage, (1450, 3300), alpha=True)

        # 绘制弹速
        initialSpeed = BuildImage(w=0, h=0, font="default.ttf", font_size=120,
                                  plain_text=f"弹速 {int(ammoInfo.initialSpeed)}m/s",
                                  is_alpha=True, font_color=(55, 55, 55))
        bg.paste(initialSpeed, (2650, 2700), alpha=True)

        # 绘制跳弹
        ricochetChanceText = "跳弹 "
        if ammoInfo.ricochetChance > 0:
            ricochetChanceText += f"+{int(ammoInfo.ricochetChance * 100)}%"
        else:
            ricochetChanceText += f"{int(ammoInfo.ricochetChance * 100)}%"
        ricochetChance = BuildImage(w=0, h=0, font="default.ttf", font_size=120, plain_text=ricochetChanceText,
                                    is_alpha=True, font_color=(55, 55, 55))
        bg.paste(ricochetChance, (2650, 2900), alpha=True)

        # 后座力修正颜色
        rMColor = (55, 55, 55)
        if ammoInfo.recoilModifier > 0:
            rMColor = (255, 0, 0)
        elif ammoInfo.recoilModifier < 0:
            rMColor = (20, 200, 20)
        # 绘制后座
        recoilModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=120, is_alpha=True, font_color=(55, 55, 55),
                                    plain_text=f"后座")
        bg.paste(recoilModifier, (2650, 3100), alpha=True)
        recoilModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=120, is_alpha=True, font_color=rMColor,
                                    plain_text=f" +{int(ammoInfo.recoilModifier * 100)}%" if ammoInfo.recoilModifier > 0 else f" {int(ammoInfo.recoilModifier * 100)}%")
        bg.paste(recoilModifier, (2890, 3100), alpha=True)

        # 精度修正颜色
        aMColor = (55, 55, 55)
        if ammoInfo.accuracyModifier > 0:
            aMColor = (20, 200, 20)
        elif ammoInfo.accuracyModifier < 0:
            aMColor = (255, 0, 0)
        # 绘制精度
        accuracyModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=120, is_alpha=True,
                                      font_color=(55, 55, 55),
                                      plain_text=f"精度")
        bg.paste(accuracyModifier, (2650, 3300), alpha=True)
        accuracyModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=120, is_alpha=True, font_color=aMColor,
                                      plain_text=f" +{int(ammoInfo.accuracyModifier * 100)}%" if ammoInfo.accuracyModifier > 0 else f" {int(ammoInfo.accuracyModifier * 100)}%")
        bg.paste(accuracyModifier, (2890, 3300), alpha=True)

        # 绘制小标题2
        title2 = BuildImage(w=0, h=0, font="default.ttf", font_size=200, plain_text="获取途径", is_alpha=True,
                            font_color=(55, 55, 55))
        bg.paste(title2, (480, 3650), alpha=True)

        # 绘制分割
        line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
        bg.paste(pos=(430, 3950), img=line, alpha=True)

        # 绘制获取源
        for i in range(0, len(ammoMoreInfo.buyFor)):

            # 获取购买需求等级与条件
            level = ammoMoreInfo.buyFor[i].requirements[0]["value"]

            # 判断头像文件是否存在
            # DLTradersLevelsImg() if not os.path.exists(path + f"traders/{ammoMoreInfo.buyFor[i].source.capitalize()}-{level}.png") else ...

            imgText = f"traders/{ammoMoreInfo.buyFor[i].source.capitalize()}-{level}.png" if ammoMoreInfo.buyFor[
                                                                                                 i].source != "fleaMarket" else "traders/fleaMarket.png "
            # 绘制源头像
            if not os.path.exists(path + imgText): DLTradersLevelsImg()
            buyForImg = BuildImage(w=640, h=640, background=path + imgText)
            bg.paste(buyForImg, (480, 4050 + i * 820), alpha=True)

            # 绘制商人名称
            tradersName = ammoMoreInfo.buyFor[i].source.capitalize() if ammoMoreInfo.buyFor[
                                                                            i].source != "fleaMarket" else "跳蚤市场"
            buyForName = BuildImage(w=0, h=0, font="default.ttf", font_size=140, plain_text=f"商人名称 {tradersName}",
                                    is_alpha=True, font_color=(55, 55, 55))
            bg.paste(buyForName, (1250, 4050 + i * 820), alpha=True)

            # 绘制任务需求
            taskRequirements = ""
            for j in range(0, len(ammoMoreInfo.buyFor[i].requirements)):
                # print(ammoMoreInfo.buyFor[i].requirements[j]["stringValue"])
                if ammoMoreInfo.buyFor[i].requirements[j]["stringValue"] is not None:
                    try:
                        data = await query_task_name(ammoMoreInfo.buyFor[i].requirements[j]["stringValue"])
                    except Exception as e:
                        taskRequirements = "ERROR:网络错误"
                        continue
                    if data == -1:
                        taskRequirements = "ERROR:网络错误"
                        continue
                    if j == 1:
                        taskRequirements = data
                    else:
                        taskRequirements += " " + data
                else:
                    taskRequirements = "无"

            text = "任务需求 " + taskRequirements if ammoMoreInfo.buyFor[i].source != "fleaMarket" else "24h均价 " + str(
                ammoMoreInfo.avg24hPrice)
            buyForRequirements = BuildImage(w=0, h=0, font="default.ttf", font_size=140, plain_text=text, is_alpha=True,
                                            font_color=(55, 55, 55))
            bg.paste(buyForRequirements, (1250, 4270 + i * 820), alpha=True)

            # 绘制价格
            buyForPriceText = ammoMoreInfo.buyFor[i].price if ammoMoreInfo.buyFor[
                                                                  i].source != "fleaMarket" else ammoMoreInfo.fleaMarketPrice
            buyForPrice = BuildImage(w=0, h=0, font="default.ttf", font_size=140,
                                     plain_text=f"价格 {buyForPriceText} ({ammoMoreInfo.buyFor[i].currency})",
                                     is_alpha=True, font_color=(55, 55, 55))
            bg.paste(buyForPrice, (1250, 4490 + i * 820), alpha=True)

            # 绘制分割
            line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
            bg.paste(pos=(430, 4750 + i * 840), img=line, alpha=True)

        # 绘制合成源
        for i in range(0, len(ammoMoreInfo.craftsFor)):
            # 绘制所需工作台等级
            craftsForLevel = BuildImage(w=0, h=0, font="default.ttf", font_size=140,
                                        plain_text=f"Level {ammoMoreInfo.craftsFor[i].level}", is_alpha=True,
                                        font_color=(55, 55, 55))
            bg.paste(craftsForLevel, (560, 4100 + len(ammoMoreInfo.buyFor) * 820 + i * 1350), alpha=True)

            # 绘制工作台Icon
            if os.path.exists(path + f"craft/{ammoMoreInfo.craftsFor[i].name}.png"):
                craftPath = path + f"craft/{ammoMoreInfo.craftsFor[i].name}.png"
            else:
                craftPath = path + f"craft/error.png"
                print("=-=" * 20)
                print(f"ERROR: {ammoMoreInfo.craftsFor[i].name} 图片不存在")
                print("=-=" * 20)
            craftsForIcon = BuildImage(w=640, h=640, background=craftPath)
            bg.paste(craftsForIcon, (480, 4300 + len(ammoMoreInfo.buyFor) * 820 + i * 1350), alpha=True)

            # 绘制所需材料及数量
            for j in range(0, len(ammoMoreInfo.craftsFor[i].requirements)):

                cow = int(j / 5)
                # print(cow)
                posY = 4150 + len(ammoMoreInfo.buyFor) * 820 + i * 1350 + cow * 600 if len(
                    ammoMoreInfo.craftsFor[i].requirements) > 5 else 4450 + len(ammoMoreInfo.buyFor) * 820 + i * 1350
                # print(posY)
                name = ammoMoreInfo.craftsFor[i].requirements[j]["name"].replace('"', "").replace(":", "").replace("/",
                                                                                                                   "").replace(
                    "\\", "").replace("*", "").replace("?", "").replace("<", "").replace(">", "").replace("|",
                                                                                                          "").replace(
                    "”", "").replace("“", "").replace("：", "").replace("？", "").replace("，", "").replace("。",
                                                                                                         "").replace(
                    "、", "").replace("；", "").replace("‘", "").replace("’", "").replace("【", "").replace("】",
                                                                                                         "").replace(
                    "！", "").replace("（", "").replace("）", "").replace("《", "").replace("》", "").replace("·",
                                                                                                         "").replace(
                    "～", "").replace(" ", "").replace(" ", "")
                if not os.path.exists(path + f"item/{name}.png"):
                    # 下载图片
                    result = requests.get(ammoMoreInfo.craftsFor[i].requirements[j]["iconLink"], timeout=30,
                                          proxies={"http":SYSTEM_PROXY})
                    if result.status_code == 200:
                        with open(path + f"item/{name}.png", 'wb') as f:
                            f.write(result.content)
                    else:
                        print("=-=" * 20)
                        print(f"请求失败,错误代码{result.status_code}")
                        print("=-=" * 20)
                        return -1

                # print(path + f"item/{ammoMoreInfo.craftsFor[i].requirements[j]['name']}.png")
                # 绘制所需材料Icon
                craftsForRequirementsIcon = BuildImage(w=320, h=320, background=path + f"item/{name}.png")
                bg.paste(craftsForRequirementsIcon, (1250 + j % 5 * 450, posY), alpha=True)

                # 绘制所需材料数量
                craftsForRequirementsCount = BuildImage(w=0, h=0, font="default.ttf", font_size=140,
                                                        plain_text=f"x{ammoMoreInfo.craftsFor[i].requirements[j]['count']}",
                                                        is_alpha=True, font_color=(55, 55, 55))
                posX = 1250 + j % 5 * 450 + int((320 - craftsForRequirementsCount.w) / 2)
                bg.paste(craftsForRequirementsCount, (posX, posY + 320), alpha=True)

            # 绘制所需时间
            h = ammoMoreInfo.craftsFor[i].duration / 3600
            m = 60 * (h - int(h))
            craftsForTime = BuildImage(w=0, h=0, font="default.ttf", font_size=140, plain_text=f"{int(h)}时{int(m)}分",
                                       is_alpha=True, font_color=(55, 55, 55))
            posX = 480 + int((640 - craftsForTime.w) / 2)
            bg.paste(craftsForTime, (posX, 4950 + len(ammoMoreInfo.buyFor) * 820 + i * 1350), alpha=True)

            # 绘制分割
            line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
            bg.paste(pos=(430, 5150 + len(ammoMoreInfo.buyFor) * 820 + i * 1350 + 150), img=line, alpha=True)
        bg.save(path + f"img/{qqId}.png")
        print("=-" * 30)
        print("子弹详细图生成完毕")
        print("=-" * 30)
        return 1


# 下载商人头像
def DLTradersLevelsImg():
    query_str = """
{
traders {
	name
    levels{
        imageLink
    }
}
}
"""
    response = requests.post('https://api.tarkov.dev/graphql', json={'query': query_str}, headers=get_user_agent(),
                             timeout=30, proxies={"http":SYSTEM_PROXY})
    if response.status_code == 200:
        result = response.json()
    else:
        print("=-" * 30)
        print(f"请求失败,错误代码{response.status_code}")
        print("=-" * 30)
        return -1
    for trader in result["data"]["traders"]:
        if trader["levels"] is not None:
            levelNum = 1
            for level in trader["levels"]:
                if level["imageLink"] is not None:
                    if not os.path.exists(path + f"traders/{trader['name'].capitalize()}-{levelNum}.png"):
                        # 下载图片
                        result = requests.get(level["imageLink"], timeout=30, proxies={"http":SYSTEM_PROXY})
                        if result.status_code == 200:
                            with open(path + f"traders/{trader['name'].capitalize()}-{levelNum}.png", 'wb') as f:
                                f.write(result.content)
                            print("=-=" * 20)
                            print(f"{trader['name'].capitalize()}-{levelNum}.png 下载成功")
                            print("=-=" * 20)
                        else:
                            print(f"请求失败,错误代码{result.status_code}")
                            return -1
                levelNum += 1
