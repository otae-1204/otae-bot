from utils.image_utils import BuildImage
from configs.path_config import IMAGE_PATH

path = IMAGE_PATH + 'tkf-bullet/'


def build_ammo_image(ammos, qqId) -> int:
    print(ammos)
    try:
        if len(ammos) == 0:
            return 0
    except Exception as e:
        print(e)
        return 0
    try:
        # 行数
        rown = 15 if len(ammos) > 15 else len(ammos)
        # 列高 = 顶内高 + (行数 * 行高) + (行数 - 1) * 行间隔 + 底内高
        ch = 30 + (rown * 85) + (rown - 1) * 13 + 20
        # 列宽 = 左内宽 + 行长 + 右内宽 338+25 = 363
        cw = 16 + 306 + 16
        # 背景高度 = 顶外高 + 列高 + 底外高
        bgh = 120 + ch + 30
        # 列数 341
        coln = int(len(ammos) / 15) if len(ammos) % 15 == 0 else int(len(ammos) / 15) + 1
        # print(coln)
        # 背景宽度 = 左外宽 + (列宽 * 列数) + (列数 - 1) * 列间隔 + 右外宽
        bgw = 30 + (cw * coln) + (coln - 1) * 25 + 30
        # 创建背景
        bg = BuildImage(w=bgw, h=bgh)
        bg1 = BuildImage(w=0, h=0, background=path + 'bg.png')
        strip = BuildImage(w=0, h=0, background=path + '长条.png')
        xn = 0 if bg.w <= 792 else int(bg.w / 792)
        yn = 0 if bg.h <= 792 else int(bg.h / 792)
        for i in range(0, xn + 1):
            for j in range(0, yn + 1):
                bg.paste(bg1, (i * 792, j * 792))
                # bg.show()

        # 按照15个一列将列表分割
        ammolist = [ammos[i:i + 15] for i in range(0, len(ammos), 15)]
        # print(ammolist)   
        bg.paste(pos=(20, 30), img=BuildImage(w=0, h=0, background=path + "查询子弹子标题.png"), alpha=True)
        # 创建列
        for i in range(0, coln):
            rown = len(ammolist[i])
            ch = 30 + (rown * 85) + (rown - 1) * 13 + 20
            # 创建列
            col = BuildImage(w=cw, h=ch, color=(161, 198, 234))
            col.circle_corner(10)
            # col.show()
            col_bg1 = BuildImage(w=cw - 4, h=ch - 4, color=(218, 227, 229))
            col_bg1.circle_corner(6)
            col.paste(col_bg1, (2, 2), alpha=True)
            # col.show()

            # 创建行
            for j in range(0, len(ammolist[i])):
                row = BuildImage(w=306, h=85, is_alpha=True, font="default.ttf", font_size=15)
                row.paste(strip, (0, 83))
                bulletimg = BuildImage(  # ammolist[i][j].bulletimg
                    w=0, h=0, is_alpha=True, background=path + "bullet/{0}".format(ammolist[i][j].img))
                # bulletimg.circle_corner(10)
                # bulletbg = BuildImage(w=64, h=64, color=(73, 81, 84),is_alpha=True)
                # bulletbg.circle_corner(10)
                # bulletbg.save(path + "text.png")
                # bulletbg.paste(bulletimg, (0, 0))

                row.paste(bulletimg, (6, 0))
                idtxt = BuildImage(w=0, h=0, font="default.ttf", font_size=13, font_color=(130, 149, 153),
                                   plain_text="id:" + str(ammolist[i][j].id), is_alpha=True)
                row.paste(idtxt, (10, 63), alpha=True)
                row.text(pos=(81, -2), text="名称 " + ammolist[i][j].name, fill=(0, 0, 0))
                row.text(pos=(81, 17), text="口径 " + ammolist[i][j].caliber, fill=(0, 0, 0))
                row.text(pos=(81, 36), text="肉伤 " + (((str(ammolist[i][j].projectileCount)+"x") \
                                                     if ammolist[i][j].projectileCount != 1 else "") + str(ammolist[i][j].damage)), fill=(0, 0, 0))
                row.text(pos=(81, 55), text="穿甲 " + str(ammolist[i][j].penetrationPower), fill=(0, 0, 0))
                accuracyModifier = round(ammolist[i][j].accuracyModifier * 100, 1)
                if accuracyModifier > 0:
                    color = (0, 255, 0)
                elif accuracyModifier < 0:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0)
                row.text(pos=(165, 36), text="精度", fill=(0, 0, 0))
                row.text(pos=(202, 36), text=("+" + str(accuracyModifier) + "%" if accuracyModifier > 0 else
                                              str(accuracyModifier) + "%"), fill=color)
                recoilModifier = round(ammolist[i][j].recoilModifier * 100, 1)
                if recoilModifier > 0:
                    color = (255, 0, 0)
                elif recoilModifier < 0:
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 0)
                row.text(pos=(165, 55), text="后座", fill=(0, 0, 0))
                row.text(pos=(202, 55), text=("+" + str(recoilModifier) + "%" if recoilModifier > 0 else
                                              str(recoilModifier) + "%"), fill=color)
                # txt = BuildImage(w=0, h=0, font="default.ttf", font_size=14, font_color=(255, 0, 0), plain_text="禁售"
                # if ammolist[i][j].marketSale == 0 else " ", is_alpha=True)
                # row.paste(txt, (260, 36), alpha=True)
                row.text(pos=(267, 36), text="禁售" if ammolist[i][j].marketSale == 0 else " ", fill=(255, 0, 0))
                color = (0, 0, 0)
                if ammolist[i][j].tracerColor == "red" or ammolist[i][j].tracerColor == "tracerRed":
                    color = (255, 0, 0)
                elif ammolist[i][j].tracerColor == "green" or ammolist[i][j].tracerColor == "tracerGreen":
                    color = (0, 255, 0)
                elif ammolist[i][j].tracerColor == "yellow":
                    color = (255, 255, 0)
                # txt1 = BuildImage(w=0, h=0, font="default.ttf", font_size=14, font_color=color, plain_text="曳光" if
                # ammolist[i][j].tracer == 0 else " ", is_alpha=True)
                # row.paste(txt1, (260, 55), alpha=True)
                row.text(pos=(265, 55), text="曳" if ammolist[i][j].tracer else " ", fill=color)
                row.text(pos=(285, 55), text="亚" if ammolist[i][j].initialSpeed <= 340 else " ", fill=(0, 0, 0))
                # row.show()
                col.paste(row, (16, 30 + j * 98), alpha=True)
            # col.show()
            bg.paste(col, (30 + i * 363, 120), alpha=True)
        bg.save(path + qqId + ".png")
        print("=-"*30)  
        print("子弹粗略图生成完毕")
        print("=-"*30) 
        return 1
    except Exception as e:
        print(e)
        return -1

        # 306 85


def build_ammo_info(ammo, qqId) -> int:
    # print(ammos)

    try:
        if len(ammos) == 0:
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
