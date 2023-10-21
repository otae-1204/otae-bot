from utils.image_utils import BuildImage
from configs.path_config import IMAGE_PATH
from configs.config import SYSTEM_PROXY
from utils.user_agent import get_user_agent
from .db import query_task_name
from .Ammo import AmmoMoreInfo
import os, requests


path = IMAGE_PATH + 'tkf-bullet/'

# 简略信息图片绘制


def build_ammo_image(ammos, qqId) -> int:

    # 判断是否有数据
    try:
        if len(ammos) == 0:
            return 0
    except Exception as e:
        print(e)
        return -1

    # 主体绘制
    try:
        # 行数
        rowN = 15 if len(ammos) > 15 else len(ammos)

        # 列高 = 顶内高 + (行数 * 行高) + (行数 - 1) * 行间隔 + 底内高
        ch = 30 + (rowN * 85) + (rowN - 1) * 13 + 20

        # 列宽 = 左内宽 + 行长 + 右内宽 338+25 = 363
        cw = 16 + 306 + 16

        # 背景高度 = 顶外高 + 列高 + 底外高
        bgh = 120 + ch + 30

        # 列数 341
        colN = int(
            len(ammos) / 15) if len(ammos) % 15 == 0 else int(len(ammos) / 15) + 1

        # 背景宽度 = 左外宽 + (列宽 * 列数) + (列数 - 1) * 列间隔 + 右外宽
        bgw = 30 + (cw * colN) + (colN - 1) * 25 + 30

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

        # 按照15个一列将列表分割
        ammoList = [ammos[i:i + 15] for i in range(0, len(ammos), 15)]

        # 拼接标题
        bg.paste(pos=(20, 30), img=BuildImage(
            w=0, h=0, background=path + "UI/查询子弹子标题.png"), alpha=True)

        # 创建列
        for i in range(0, colN):
            rowN = len(ammoList[i])
            ch = 30 + (rowN * 85) + (rowN - 1) * 13 + 20

            # 创建列背景
            col = BuildImage(w=cw, h=ch, color=(161, 198, 234))
            col.circle_corner(10)
            col_bg1 = BuildImage(w=cw - 4, h=ch - 4, color=(218, 227, 229))
            col_bg1.circle_corner(6)

            # 拼接列背景
            col.paste(col_bg1, (2, 2), alpha=True)

            # 创建行
            for j in range(0, len(ammoList[i])):
                # 创建行背景
                row = BuildImage(w=306, h=85, is_alpha=True,
                                 font="default.ttf", font_size=15)

                # 拼接长条
                row.paste(strip, (0, 83))

                # 创建并粘贴子弹图片
                bulletImg = BuildImage(
                    w=0, h=0, is_alpha=True, background=path + f"bullet/{ammoList[i][j].img}")
                row.paste(bulletImg, (6, 0))

                # 创建并粘贴子弹信息
                idTxt = BuildImage(w=0, h=0, font="default.ttf", font_size=13, font_color=(
                    130, 149, 153), plain_text="id:" + str(ammoList[i][j].id), is_alpha=True)
                row.paste(idTxt, (10, 63), alpha=True)
                row.text(pos=(81, -2), text="名称 " +
                         ammoList[i][j].name, fill=(0, 0, 0))
                row.text(pos=(81, 17), text="口径 " +
                         ammoList[i][j].caliber, fill=(0, 0, 0))
                row.text(pos=(81, 36), text="肉伤 " + (((str(ammoList[i][j].projectileCount)+"x")
                                                     if ammoList[i][j].projectileCount != 1 else "") + str(ammoList[i][j].damage)), fill=(0, 0, 0))
                row.text(pos=(81, 55), text="穿甲 " +
                         str(ammoList[i][j].penetrationPower), fill=(0, 0, 0))
                accuracyModifier = round(
                    ammoList[i][j].accuracyModifier * 100, 1)
                
                # 精度修正颜色
                if accuracyModifier > 0:
                    color = (0, 255, 0)
                elif accuracyModifier < 0:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0)
                row.text(pos=(165, 36), text="精度", fill=(0, 0, 0))
                row.text(pos=(202, 36), text=("+" + str(accuracyModifier) + "%" if accuracyModifier > 0 else
                                              str(accuracyModifier) + "%"), fill=color)
                recoilModifier = round(ammoList[i][j].recoilModifier * 100, 1)

                # 后座力修正颜色
                if recoilModifier > 0:
                    color = (255, 0, 0)
                elif recoilModifier < 0:
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 0)
                row.text(pos=(165, 55), text="后座", fill=(0, 0, 0))
                row.text(pos=(202, 55), text=("+" + str(recoilModifier) + "%" if recoilModifier > 0 else
                                              str(recoilModifier) + "%"), fill=color)
                row.text(pos=(
                    267, 36), text="禁售" if ammoList[i][j].marketSale == 0 else " ", fill=(255, 0, 0))
                color = (0, 0, 0)

                # 弹迹颜色
                if ammoList[i][j].tracerColor == "red" or ammoList[i][j].tracerColor == "tracerRed":
                    color = (255, 0, 0)
                elif ammoList[i][j].tracerColor == "green" or ammoList[i][j].tracerColor == "tracerGreen":
                    color = (0, 255, 0)
                elif ammoList[i][j].tracerColor == "yellow":
                    color = (255, 255, 0)
                row.text(
                    pos=(265, 55), text="曳" if ammoList[i][j].tracer else " ", fill=color)
                row.text(pos=(
                    285, 55), text="亚" if ammoList[i][j].initialSpeed <= 340 else " ", fill=(0, 0, 0))
                
                # 粘贴行
                col.paste(row, (16, 30 + j * 98), alpha=True)
            
            # 粘贴列
            bg.paste(col, (30 + i * 363, 120), alpha=True)

        # 保存图片
        bg.save(path + f"img/{qqId}.png")
        print("=-"*30)
        print("子弹粗略图生成完毕")
        print("=-"*30)
        return 1
    except Exception as e:
        print(e)
        return -1


def build_ammo_info(ammoInfo, ammoMoreInfo: AmmoMoreInfo, qqId) -> int:
        if ammoInfo != None:
            # 获取画布宽度 30 + 30 + 340
            bgw = 393

            # 获取画布高度 顶外高 + 列高(280 + 30 + 商人获取渠道数*110 + 工作台获取渠道数*135) + 底外高
            bgh = 120 + 240 + 20 + len(ammoMoreInfo.buyFor)*85 + len(ammoMoreInfo.craftsFor)*135 + 35 + 30
            
            # 创建画布
            bg = BuildImage(w=bgw, h=bgh, color=(55, 55, 55),font="default.ttf", font_size=15)

            # 填充背景图片
            bg1 = BuildImage(w=0, h=0, background=path + 'UI/bg.png')
            xn = 0 if bg.w <= 792 else int(bg.w / 792)
            yn = 0 if bg.h <= 792 else int(bg.h / 792)
            for i in range(0, xn + 1):
                for j in range(0, yn + 1):
                    bg.paste(bg1, (i * 792, j * 792))

            # 绘制标题
            bg.paste(pos=(20, 30), img=BuildImage(w=0, h=0, background=path + "UI/查询子弹子标题.png"), alpha=True)

            # 绘制信息背景外部
            infoBg = BuildImage(w=bgw - 60, h=bgh-150, color=(161, 198, 234))

            # 绘制信息背景外部圆角
            infoBg.circle_corner(10)

            # 绘制信息背景内部
            infoBg1 = BuildImage(w=bgw - 64, h=bgh-154, color=(218, 227, 229))

            # 绘制信息背景内部圆角
            infoBg1.circle_corner(6)

            # 拼接信息背景
            infoBg.paste(infoBg1, (2, 2), alpha=True)

            # 绘制信息背景
            bg.paste(infoBg, (30, 120), alpha=True)

            # 绘制子弹文字
            title = BuildImage(w=0, h=0, font="default.ttf", font_size=20, plain_text="子弹数据", is_alpha=True, font_color=(55, 55, 55))
            bg.paste(title, (48, 135),alpha=True)

            # 绘制长条分割线
            line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
            bg.paste(pos=(43, 165), img=line, alpha=True)

            # 绘制子弹图片
            img = BuildImage(w=0, h=0, background=path + f"bullet/{ammoInfo.img}")
            img.circle_corner(6)
            bg.paste(pos=(55, 183), img=img, alpha=True)        

            # 绘制子弹名称
            name = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text="名称 " + ammoInfo.name, is_alpha=True, font_color=(55, 55, 55))
            bg.paste(name, (133, 186),alpha=True)

            # 绘制子弹口径
            caliber = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text="口径 " + ammoInfo.caliber, is_alpha=True, font_color=(55, 55, 55))
            bg.paste(caliber, (133, 207),alpha=True)

            # 绘制子弹类型
            typeName = ""
            damageList = ammoInfo.damage.split("x") if type(ammoInfo.damage) == str else [ammoInfo.damage]
            if len(damageList) == 2:
                damage = damageList[0] * damageList[1]
            else:
                damage = damageList[0]
            typeName += "肉伤弹 " if int(damage) > 75 and ammoInfo.penetrationPower < 20 else ""
            typeName += "高级穿甲弹 " if ammoInfo.penetrationPower >= 50 and ammoInfo.penetrationPower < 60 else ""
            typeName += "顶级穿甲弹 " if ammoInfo.penetrationPower >= 60 else ""
            typeName += "亚音速弹" if ammoInfo.initialSpeed < 340 else ""
            typeImg = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text="类型 " + typeName, is_alpha=True, font_color=(55, 55, 55))
            bg.paste(typeImg, (133, 228),alpha=True)

            # 绘制子弹id
            id = BuildImage(w=0, h=0, font="default.ttf", font_size=10, plain_text="id: " + str(ammoInfo.id), is_alpha=True, font_color=(60, 60, 60))
            bg.paste(id, (60, 247),alpha=True)
            
            # 绘制子弹肉伤
            damage = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text="子弹肉伤 " + str(ammoInfo.damage), is_alpha=True, font_color=(55, 55, 55))
            bg.paste(damage, (47, 270),alpha=True)

            # 绘制子弹穿甲
            armorDamage = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text="子弹穿甲 " + str(ammoInfo.armorDamage), is_alpha=True, font_color=(55, 55, 55))
            bg.paste(armorDamage, (47, 290),alpha=True)

            # 绘制子弹最大堆叠
            stackMaxSize = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text="最大堆叠 " + str(ammoInfo.stackMaxSize), is_alpha=True, font_color=(55, 55, 55))
            bg.paste(stackMaxSize, (47, 310),alpha=True)

            # 绘制曳光颜色
            colorName = "无"
            if ammoInfo.tracer:
                if ammoInfo.tracerColor == "red" or ammoInfo.tracerColor == "tracerRed":
                    colorName = "红"
                elif ammoInfo.tracerColor == "green" or ammoInfo.tracerColor == "tracerGreen":
                    colorName = "绿"
                elif ammoInfo.tracerColor == "yellow":
                    colorName = "黄"
            tracerColor = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text="曳光颜色 " + colorName, is_alpha=True, font_color=(55, 55, 55))
            bg.paste(tracerColor, (47, 330),alpha=True)

            # 绘制小出血修正
            lightBleedModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text= f"小出血修正 {int(ammoInfo.lightBleedModifier * 100)}%",
                                            is_alpha=True, font_color=(55, 55, 55))
            bg.paste(lightBleedModifier, (145, 270),alpha=True)

            # 绘制大出血修正
            heavyBleedModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text= f"大出血修正 {int(ammoInfo.heavyBleedModifier * 100)}%",
                                            is_alpha=True, font_color=(55, 55, 55))
            bg.paste(heavyBleedModifier, (145, 290),alpha=True)

            # 绘制受伤掉耐
            staminaBurnPerDamage = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text= f"被击打掉耐 {int(ammoInfo.staminaBurnPerDamage * 100)}%",
                                              is_alpha=True, font_color=(55, 55, 55))
            bg.paste(staminaBurnPerDamage, (145, 310),alpha=True)

            # 绘制护甲损伤
            armorDamage = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text= f"对护甲损伤 {int(ammoInfo.armorDamage)}%",
                                     is_alpha=True, font_color=(55, 55, 55))
            bg.paste(armorDamage, (145, 330),alpha=True)

            # 绘制弹速
            initialSpeed = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text= f"弹速 {int(ammoInfo.initialSpeed)}m/s",
                                      is_alpha=True, font_color=(55, 55, 55))
            bg.paste(initialSpeed, (265, 270),alpha=True)

            # 绘制跳弹
            ricochetChance = BuildImage(w=0, h=0, font="default.ttf", font_size=12, plain_text= "跳弹 " + f"+{int(ammoInfo.ricochetChance * 100)}%" if ammoInfo.ricochetChance > 0 else f"{int(ammoInfo.ricochetChance * 100)}%",
                                        is_alpha=True, font_color=(55, 55, 55))
            bg.paste(ricochetChance, (265, 290),alpha=True)
            
            # 后座力修正颜色
            rMColor = (55, 55, 55)
            if ammoInfo.recoilModifier > 0:
                rMColor = (255, 0, 0)
            elif ammoInfo.recoilModifier < 0:
                rMColor = (20, 200, 20)
            # 绘制后座
            recoilModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=12, is_alpha=True, font_color=(55, 55, 55), 
                                        plain_text= f"后座")
            bg.paste(recoilModifier, (265, 310),alpha=True)
            recoilModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=12, is_alpha=True, font_color=rMColor, 
                                        plain_text= f" +{int(ammoInfo.recoilModifier * 100)}%" if ammoInfo.recoilModifier > 0 else f" {int(ammoInfo.recoilModifier * 100)}%")
            bg.paste(recoilModifier, (289, 310),alpha=True)

            # 精度修正颜色
            aMColor = (55, 55, 55)
            if ammoInfo.accuracyModifier > 0:
                aMColor = (20, 200, 20)
            elif ammoInfo.accuracyModifier < 0:
                aMColor = (255, 0, 0)
            # 绘制精度
            accuracyModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=12, is_alpha=True, font_color=(55, 55, 55), 
                                          plain_text= f"精度")
            bg.paste(accuracyModifier, (265, 330),alpha=True)
            accuracyModifier = BuildImage(w=0, h=0, font="default.ttf", font_size=12, is_alpha=True, font_color=aMColor, 
                                          plain_text= f" +{int(ammoInfo.accuracyModifier * 100)}%" if ammoInfo.accuracyModifier > 0 else f" {int(ammoInfo.accuracyModifier * 100)}%")
            bg.paste(accuracyModifier, (289, 330),alpha=True)

            # 绘制小标题2
            title2 = BuildImage(w=0, h=0, font="default.ttf", font_size=20, plain_text="获取途径", is_alpha=True, font_color=(55, 55, 55))
            bg.paste(title2, (48, 365),alpha=True)

            # 绘制分割
            line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
            bg.paste(pos=(43, 395), img=line, alpha=True)

            # 绘制获取源
            for i in range(0, len(ammoMoreInfo.buyFor)):

                # 获取购买需求等级与条件
                level = ammoMoreInfo.buyFor[i].requirements[0]["value"]

                # 判断头像文件是否存在
                if not os.path.exists(path + f"traders/{ammoMoreInfo.buyFor[i].source.capitalize()}-{level}.png"):
                    if DLTradersLevelsImg() == -1:
                        return -1
                
                imgText = f"traders/{ammoMoreInfo.buyFor[i].source}-{level}.png" if ammoMoreInfo.buyFor[i].source != "fleaMarket" else "traders/fleaMarket.png"
                # 绘制源头像
                buyForImg = BuildImage(w=64, h=64, background = path + imgText)
                bg.paste(buyForImg, (48, 405 + i * 82),alpha=True)

                # 绘制商人名称
                tradersName = ammoMoreInfo.buyFor[i].source.capitalize() if ammoMoreInfo.buyFor[i].source != "fleaMarket" else "跳蚤市场"
                buyForName = BuildImage(w=0, h=0, font="default.ttf", font_size=14, plain_text=f"商人名称 {tradersName}", is_alpha=True, font_color=(55, 55, 55))
                bg.paste(buyForName, (125, 405 + i * 82),alpha=True)

                # 绘制任务需求
                taskRequirements = ""
                for j in range(0,len(ammoMoreInfo.buyFor[i].requirements)):
                    print(ammoMoreInfo.buyFor[i].requirements[j]["stringValue"])
                    if ammoMoreInfo.buyFor[i].requirements[j]["stringValue"] != None:
                        try:
                            data = query_task_name(ammoMoreInfo.buyFor[i].requirements[j]["stringValue"])
                        except Exception as e:
                            taskRequirements = "ERROR:网络错误"
                            continue
                        if data == -1:
                            taskRequirements = "ERROR:网络错误"
                            continue
                        if(j == 1):
                            taskRequirements = data 
                        else:
                            taskRequirements += " " + data
                    else:
                        taskRequirements = "无"

                text = "任务需求 " + taskRequirements if ammoMoreInfo.buyFor[i].source != "fleaMarket" else "24h均价 " + str(ammoMoreInfo.avg24hPrice)
                buyForRequirements = BuildImage(w=0, h=0, font="default.ttf", font_size=14, plain_text=text, is_alpha=True, font_color=(55, 55, 55))
                bg.paste(buyForRequirements, (125, 427 + i * 82),alpha=True)

                # 绘制价格
                buyForPrice = BuildImage(w=0, h=0, font="default.ttf", font_size=14, plain_text=f"价格 {ammoMoreInfo.buyFor[i].price} ({ammoMoreInfo.buyFor[i].currency})",is_alpha=True, font_color=(55, 55, 55))
                bg.paste(buyForPrice, (125, 449 + i * 82),alpha=True)

                # 绘制分割
                line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
                bg.paste(pos=(43, 475 + i * 84), img=line, alpha=True)

            # 绘制合成源
            for i in range(0, len(ammoMoreInfo.craftsFor)):
                # 绘制所需工作台等级
                craftsForLevel = BuildImage(w=0, h=0, font="default.ttf", font_size=14, plain_text=f"Level {ammoMoreInfo.craftsFor[i].level}",is_alpha=True, font_color=(55, 55, 55))
                bg.paste(craftsForLevel, (56, 410 + len(ammoMoreInfo.buyFor) * 82 + i * 135),alpha=True)

                # 绘制工作台Icon
                if(os.path.exists(path + f"craft/{ammoMoreInfo.craftsFor[i].name}.png")):
                    craftPath = path + f"craft/{ammoMoreInfo.craftsFor[i].name}.png"
                else:
                    craftPath = path + f"craft/error.png"
                    print(f"ERROR: {ammoMoreInfo.craftsFor[i].name} 图片不存在")
                craftsForIcon = BuildImage(w=64, h=64, background = craftPath)
                bg.paste(craftsForIcon, (48, 430 + len(ammoMoreInfo.buyFor) * 82 + i * 135),alpha=True)
                
                # 绘制所需材料及数量
                for j in range(0, len(ammoMoreInfo.craftsFor[i].requirements)):
                    
                    cow = int(j / 5)
                    print(cow)
                    posY = 415 + len(ammoMoreInfo.buyFor) * 82 + i * 135 + cow * 60 if len(ammoMoreInfo.craftsFor[i].requirements) > 5 else 445 + len(ammoMoreInfo.buyFor) * 82 + i * 135
                    print(posY)
                    name = ammoMoreInfo.craftsFor[i].requirements[j]["name"].replace('"',"").replace(":","").replace("/","").replace("\\","").replace("*","").replace("?","").replace("<","").replace(">","").replace("|","").replace("”","").replace("“","").replace("：","").replace("？","").replace("，","").replace("。","").replace("、","").replace("；","").replace("‘","").replace("’","").replace("【","").replace("】","").replace("！","").replace("（","").replace("）","").replace("《","").replace("》","").replace("·","").replace("～","").replace(" ","").replace(" ","")
                    if not os.path.exists(path + f"item/{name}.png"):
                        # 下载图片
                        result = requests.get(ammoMoreInfo.craftsFor[i].requirements[j]["iconLink"], timeout=30, proxies=SYSTEM_PROXY)
                        if result.status_code == 200:
                            with open(path + f"item/{name}.png", 'wb') as f:
                                f.write(result.content)
                        else:
                            print(f"请求失败,错误代码{result.status_code}")
                            return -1
                    
                    # print(path + f"item/{ammoMoreInfo.craftsFor[i].requirements[j]['name']}.png")
                    # 绘制所需材料Icon
                    craftsForRequirementsIcon = BuildImage(w=32, h=32, background = path + f"item/{name}.png")
                    bg.paste(craftsForRequirementsIcon, (125 + j % 5 * 45, posY),alpha=True)

                    # 绘制所需材料数量
                    craftsForRequirementsCount = BuildImage(w=0, h=0, font="default.ttf", font_size=14, plain_text=f"x{ammoMoreInfo.craftsFor[i].requirements[j]['count']}",is_alpha=True, font_color=(55, 55, 55))
                    posX = 125 + j % 5 * 45 + int((32 - craftsForRequirementsCount.w) / 2)
                    bg.paste(craftsForRequirementsCount, (posX, posY+32),alpha=True)

                # 绘制所需时间
                h = ammoMoreInfo.craftsFor[i].duration / 3600
                m = 60 * (h - int(h))
                craftsForTime = BuildImage(w=0, h=0, font="default.ttf", font_size=14, plain_text=f"{int(h)}时{int(m)}分",is_alpha=True, font_color=(55, 55, 55))
                posX = 48 + int((64 - craftsForTime.w) / 2)
                bg.paste(craftsForTime, (posX, 495 + len(ammoMoreInfo.buyFor) * 82 + i * 135),alpha=True)

                # 绘制分割
                line = BuildImage(w=0, h=0, background=path + "UI/详细信息长条.png")
                bg.paste(pos=(43, 515 + len(ammoMoreInfo.buyFor) * 82 + i * 135 + 15), img=line, alpha=True)
            bg.save(path + f"img/{qqId}.png")
            print("=-"*30)
            print("子弹详细图生成完毕")
            print("=-"*30)
            return 1




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
    response = requests.post('https://api.tarkov.dev/graphql', json={'query': query_str}, headers=get_user_agent(), timeout=30, proxies=SYSTEM_PROXY)
    if response.status_code == 200:
        result = response.json()
    else:
        print(f"请求失败,错误代码{response.status_code}")
        return -1
    for trader in result["data"]["traders"]:
        if trader["levels"] != None:
            levelNum = 1
            for level in trader["levels"]:
                if level["imageLink"] != None:
                    if not os.path.exists(path + f"traders/{trader['name'].capitalize()}-{levelNum}.png"):
                        # 下载图片
                        result = requests.get(level["imageLink"], timeout=30, proxies=SYSTEM_PROXY)
                        if result.status_code == 200:
                            with open(path + f"traders/{trader['name'].capitalize()}-{levelNum}.png", 'wb') as f:
                                f.write(result.content)
                        else:
                            print(f"请求失败,错误代码{result.status_code}")
                            return -1
                levelNum+=1




#
# ammo = Ammo("M856", "7.62x51", 1, 2, False, "green",
#             "10", 20, 30, 40, 50, 0.6, 0.7, 80, 90, "test.png", 0)
#
# ammos = [ammo]
# for i in range(0, 10):
#     ammos.append(ammo)
#
# build_ammo_image(ammos,"11111")
