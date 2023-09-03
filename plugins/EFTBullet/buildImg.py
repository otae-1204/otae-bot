from utils.image_utils import BuildImage
from configs.path_config import IMAGE_PATH
from .Ammo import AmmoMoreInfo


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
        bg1 = BuildImage(w=0, h=0, background=path + 'bg.png')

        # 创建长条
        strip = BuildImage(w=0, h=0, background=path + '长条.png')

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
            w=0, h=0, background=path + "查询子弹子标题.png"), alpha=True)

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
                    w=0, h=0, is_alpha=True, background=path + "bullet/{0}".format(ammoList[i][j].img))
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
        bg.save(path + qqId + ".png")
        print("=-"*30)
        print("子弹粗略图生成完毕")
        print("=-"*30)
        return 1
    except Exception as e:
        print(e)
        return -1


def build_ammo_info(ammosInfo, ammoMoreInfo: AmmoMoreInfo, qqId) -> int:
    try:
        if len(ammosInfo) == 0:
            # 获取画布宽度 30 + 30 + 340
            bgw = 400
            
            # 获取画布高度 顶外高 + 列高(280 + 30 + 商人获取渠道数*100 + 工作台获取渠道数*150) + 底外高
            bgh = 120 + 280 + 30 + len(ammoMoreInfo.buyFor) + len(ammoMoreInfo.craftsFor) + 30
            
            # 创建画布
            bg = BuildImage(w=bgw, h=bgh)

            # 填充背景图片
            bg1 = BuildImage(w=0, h=0, background=path + 'bg.png')
            xn = 0 if bg.w <= 792 else int(bg.w / 792)
            yn = 0 if bg.h <= 792 else int(bg.h / 792)
            for i in range(0, xn + 1):
                for j in range(0, yn + 1):
                    bg.paste(bg1, (i * 792, j * 792))

            # 绘制标题
            bg.paste(pos=(20, 30), img=BuildImage(w=0, h=0, background=path + "查询子弹子标题.png"), alpha=True)

            # 绘制信息背景
            infoBg = BuildImage(w=bgw - 60, h=280, color=(161, 198, 234))


            


            
            return 0
    except Exception as e:
        print(e)
        return 0
    

#
# ammo = Ammo("M856", "7.62x51", 1, 2, False, "green",
#             "10", 20, 30, 40, 50, 0.6, 0.7, 80, 90, "test.png", 0)
#
# ammos = [ammo]
# for i in range(0, 10):
#     ammos.append(ammo)
#
# build_ammo_image(ammos,"11111")
