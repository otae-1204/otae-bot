from PIL import Image
from matplotlib import image
from utils.image_utils import BuildImage
from configs.path_config import IMAGE_PATH

def ApexRankImg(
        RPtxt:list,
        APtxt:list,
        RPImg:image,
        APImg:image):

    # 创建背景图
    bimg = BuildImage(w=0,h=0,background=IMAGE_PATH+"apex/bg.png",font_size=24)
    # 打开RP图片
    imgRP = Image.open(f"{IMAGE_PATH}apex/{RPImg}")
    # 计算RP图位置
    h = int(175 + ((120 - imgRP.height)/2))
    w = int(129 + ((120 - imgRP.width)/2))
    imgRpPos = (w,h)
    # 往背景上贴RP图
    bimg.paste(img=imgRP,pos=imgRpPos,alpha=True)
    # 打开AP图
    imgAP = Image.open(f"{IMAGE_PATH}apex/{APImg}")
    # 计算AP图位置
    h = int(175 + ((120 - imgRP.height)/2))
    w = int(411 + ((120 - imgRP.width)/2))
    imgApPos = (w,h)
    #往背景贴AP图
    bimg.paste(img=imgAP,pos=imgApPos,alpha=True)

    10000
    5000
    "大师/APEX猎杀者"
    11451
    5000
    10000
    "白金Ⅳ"

    # 定义回复
    # txt = ["您的RP分数为",f"{RP}分","距上次查询分差",f"{lastRP-RP}分",f"属于“{RPRank}","历史查询最高分",f"{maxRank}分"]

    # 生成RP文字底板
    RPtxtImg = BuildImage(w=380,h=len(RPtxt)*40,font_size=24,is_alpha=True)
    # 生成RP文字图片
    for i in range(0,len(RPtxt)):
        # print(RPtxt[i])
        RPtxtImg.text(pos=(1,i*40),text=RPtxt[i],fill=(0,119,221),center_type="by_width")
    # 粘贴RP文字
    bimg.paste(img=RPtxtImg,pos=[0,316],alpha=True)

    # 生成AP文字底板
    APtxtImg = BuildImage(w=380,h=len(APtxt)*40,font_size=24,is_alpha=True)
    # 生成AP文字图片
    for i in range(0,len(APtxt)):
        # print(APtxt[i])
        APtxtImg.text(pos=(1,i*40),text=APtxt[i],fill=(0,119,221),center_type="by_width")
    # 粘贴AP文字
    bimg.paste(img=APtxtImg,pos=[279,316],alpha=True)


def ImgRPBuild(RPtxt:list,RPImg:str,bgimg:BuildImage):
    # 打开RP图片
    imgRP = Image.open(f"{IMAGE_PATH}apex/{RPImg}")
    # 计算RP图位置
    h = int(175 + ((120 - imgRP.height)/2))
    w = int(129 + ((120 - imgRP.width)/2))
    imgRpPos = (w,h)
    # 往背景上贴RP图
    bgimg.paste(img=imgRP,pos=imgRpPos,alpha=True)
    # 生成RP文字底板
    RPtxtImg = BuildImage(w=380,h=len(RPtxt)*40,font_size=24,is_alpha=True)
    # 生成RP文字图片
    for i in range(0,len(RPtxt)):
        # print(RPtxt[i])
        RPtxtImg.text(pos=(1,i*40),text=RPtxt[i],fill=(0,119,221),center_type="by_width")
    # 粘贴RP文字
    bgimg.paste(img=RPtxtImg,pos=[0,316],alpha=True)
    return bgimg

def ImgAPBuild(APtxt:list,APImg:str,bgimg:BuildImage):
    # 打开AP图
    imgAP = Image.open(f"{IMAGE_PATH}apex/{APImg}")
    # 计算AP图位置
    h = int(175 + ((120 - imgAP.height)/2))
    w = int(411 + ((120 - imgAP.width)/2))
    imgApPos = (w,h)
    #往背景贴AP图
    bgimg.paste(img=imgAP,pos=imgApPos,alpha=True)
    # 生成AP文字底板
    APtxtImg = BuildImage(w=380,h=len(APtxt)*40,font_size=24,is_alpha=True)
    # 生成AP文字图片
    for i in range(0,len(APtxt)):
        # print(APtxt[i])
        APtxtImg.text(pos=(1,i*40),text=APtxt[i],fill=(0,119,221),center_type="by_width")
    # 粘贴AP文字
    bgimg.paste(img=APtxtImg,pos=[279,316],alpha=True)
    return bgimg
