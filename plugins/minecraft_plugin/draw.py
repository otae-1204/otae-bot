# from utils.image_utils import PILBuildImage
from configs.path_config import IMAGE_PATH, FONT_PATH
from pil_utils import BuildImage, Text2Image
from io import BytesIO
import re
import base64

path = IMAGE_PATH + "minecraft_plugin/"
ttf = "mc.ttf"

def draw_server_info(server_info: dict) -> BuildImage:
    """
    说明:
        绘制服务器信息
    参数:
        :param server_info: 服务器信息
    返回:
        :return: BuildImage 对象
    """

    # 创建一个576x64的图片
    img = BuildImage.new("RGBA", (5760, 640), (0, 0, 0, 0))

    
    # 获取服务器名称
    name_text = server_info.get("name") + f"({server_info.get('nickname')})" if server_info.get("nickname") is not None else server_info.get("name")
    
    # 判断名称是否超过上限,超过则不显示昵称
    if len(name_text) > 40:
        name_text = server_info.get("name")
    
    # 绘制服务器名称
    img.draw_text(
        xy=(690, 0), 
        text=name_text, 
        fontname="Minecraft AE", 
        fontsize=165, 
        fill="white",
        halign="left",
        font_fallback=False,
    )

    # 绘制服务器地址
    img.draw_text(
        xy=(690, 240), 
        text=f"Address: {server_info.get('address')}", 
        fontname="Minecraft AE", 
        fontsize=145, 
        fill="#aaaaaa",
        halign="left",
        font_fallback=False,
    )

    
    # 确定icon图片
    if server_info["status"] == "success" and server_info["data"].get("favicon") is not None:
        icon_data = server_info["data"].get("favicon")
        icon_data = base64.b64decode(icon_data)
        icon = BytesIO(icon_data)
    else:
        icon = path + "unknown_server.png"

    # 绘制icon
    icon = BuildImage.open(icon)
    icon = icon.resize(size=(640,640), keep_ratio=True)
    img.paste(icon, (0, 0), alpha=True)

    # 判断延迟档位(0-200+分为四档)
    if server_info["status"] == "success":
        latency_num = server_info["data"].get("latency")
        if latency_num <= 50:
            latency_img = path + "latency_5.png"
        elif latency_num <= 100:
            latency_img = path + "latency_4.png"
        elif latency_num <= 150:
            latency_img = path + "latency_3.png"
        elif latency_num <= 200:
            latency_img = path + "latency_2.png"
        elif latency_num > 200:
            latency_img = path + "latency_1.png"
    else:
        latency_img = path + "latency_unknown.png"

    # 绘制延迟
    latency = BuildImage.open(latency_img)
    # 调整大小
    latency = latency.resize(size=(200,160), keep_ratio=True)
    # 粘贴  
    img.paste(latency, (5760-230, 0), alpha=True)

    # 如果服务器未开启则绘制错误信息
    if server_info["status"] != "success":
        img.draw_text(
            xy=(690, 445), 
            text=f"无法连接到服务器", 
            fontname="Minecraft AE", 
            fontsize=145, 
            fill="#fc0000",
            halign="left",
            font_fallback=False,
        )
        return img
        # output: ByteIo
        # output = img.save_png()

        # return base64.b64encode(output.getvalue()).decode()


    # 绘制服务器motd
    motd = server_info["data"].get("motd")

    # 去除颜色代码
    motd = re.sub(r"\u00a7[0-9a-fA-F]", "", motd)

    # 判断motd是否超过上限
    if len(motd) > 40:
        motd = motd[:40] + "..."

    # 绘制服务器motd
    img.draw_text(
        xy=(690, 445), 
        text=f"{motd}", 
        fontname="Minecraft AE", 
        fontsize=145, 
        fill="#808080",
        halign="left",
        font_fallback=False,
    )



    # 绘制服务器在线玩家数量
    online_players = f"{server_info['data'].get('online_players')}/{server_info['data'].get('max_players')}"
    op_img = Text2Image.from_text(
        text=online_players,
        fontname="Minecraft AE",
        fontsize=145,
        fill="#aaaaaa",
        font_fallback=False,
    ).to_image()

    # 粘贴
    img.paste(op_img, (5760-260-op_img.width, 30), alpha=True)

    # 绘制版本信息
    v_img = Text2Image.from_text(
        text=server_info['data'].get('game_version'),
        fontname="Minecraft AE",
        fontsize=145,
        fill="#aaaaaa",
        font_fallback=False,
    ).to_image()

    # 粘贴
    img.paste(v_img, (5760-30-v_img.width, 645-40-v_img.height), alpha=True)

    return img


def draw_server_list(server_info_imgs: list[BuildImage], group_name: str) -> str:
    """
    说明:
        绘制服务器列表
    参数:
        :param server_info_imgs: 服务器信息图片列表
        :param group_name: 群名
    返回:
        :return: Base64编码的图像数据
    """
    # 创建背景
    server_len = len(server_info_imgs)
    if server_len < 3:
        server_len = 3
    img_y = (640 * server_len) + (50 * 2) + (640 * 2) + (70 * (server_len-1))

    img = BuildImage.new("RGBA", (7680,img_y), (0, 0, 0, 0))

    # 粘贴背景
    bg = BuildImage.open(path + "body_bg.png")
    bg = bg.resize(size=(7680, 640), keep_ratio=True)
    for i in range(0, img_y, 640):
        img.paste(bg, (0, i), alpha=True)

    # 粘贴上下边框
    border = BuildImage.open(path + "head_bg.png")
    border = border.resize(size=(7680, 640), keep_ratio=True)
    img.paste(border, (0, 0), alpha=True)
    img.paste(border, (0, img_y-640), alpha=True)

    # 绘制群名
    group_name_img = Text2Image.from_text(
        text=group_name,
        fontname="Minecraft AE",
        fontsize=220,
        fill="white",
        font_fallback=False,
    ).to_image()

    # 粘贴
    img.paste(group_name_img, (3840-int(group_name_img.width/2), 250), alpha=True)

    # 绘制服务器列表
    for i, server_info_img in enumerate(server_info_imgs):
        y = 640*(i+1) + 50 + i*70
        img.paste(server_info_img, (960, y), alpha=True)

    # # 绘制服务器列表
    # for i, server_info_img in enumerate(server_info_imgs):
    #     img.paste(server_info_img, (0, 640*i), alpha=True)

    # output: ByteIo
    output = img.save_png()
    return output

    # return base64.b64encode(output.getvalue()).decode()


def draw_button():
    """
    说明:
        绘制按钮
    """
    text = "输入/as添加服务器"
    img = Text2Image.from_text(
        text=text,
        fontname="Minecraft AE",
        fontsize=150,
        fill="white",
        font_fallback=False,
    ).to_image()
    
    button_img = BuildImage.open(path + "button.png")
    button_img = button_img.resize(
        size=(img.width+250, img.height+200), 
        keep_ratio=True,
        inside=True
        )
    button_img.paste(img, (125, 100), alpha=True)
    # button_img.show()
    # 转换成base64
    print(button_img.width, button_img.height)
    output = button_img.save_png()
    return base64.b64encode(output.getvalue()).decode()
    # return button_img