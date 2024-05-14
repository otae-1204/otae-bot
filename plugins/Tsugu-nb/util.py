import json,re,httpx
from .entity import Config,User

config = Config()



def is_car(message: str) -> bool:
    """判断消息是否为车牌指令

    Args:
        message (str): 用户发送的消息

    Returns:
        bool: 是否为车牌指令
    """
    is_car = False

    # 检查car_config['car']中的关键字
    for keyword in config.car_config["car"]:
        if keyword in message:
            is_car = True
            break

    # 检查car_config['fake']中的关键字
    for keyword in config.car_config["fake"]:
        if keyword in message:
            is_car = False
            break

    pattern = r"^\d{5}(\D|$)|^\d{6}(\D|$)"
    if re.match(pattern, message):
        pass
    else:
        is_car = False

    return is_car

def is_command(message: str):
    """判断消息是否为命令

    Args:
        message (str): 用户发送的消息

    Returns:
        dict: 是否为命令 {"status": bool, "command": str, "message": str}
    """
    for cmd in config.cmd_list:
        for key in cmd["command_name"]:
            if message.startswith(key) and bool(cmd["ifEnable"]):
                print(f"检测到命令{cmd['name']}，消息为{message}")
                msg_text = message.replace(key, "").lstrip()
                print(f"处理后消息为{message}")
                return {"status": True, "command": cmd["name"], "message": msg_text}
    return {"status": False, "command": None, "message": message}

def get_server_index(server_name: str) -> None | int:
    """
    获取服务器索引
    
    Args:
        server_name (str): 服务器名称
    
    Returns:
        None | int: 服务器索引
    """
    for i in config.server_list:
        if server_name.strip() in config.server_list[i]:
            return int(i)
    return None


async def apost_api(api: str, data: dict) -> dict:
    """从后端API获取数据

    Args:
        api (str): API地址
        params (dict): 请求参数

    Returns:
        dict: 返回数据
    """
    try:
    # data = json.dumps(data)
        print(f"请求API为{api}\n,请求数据为{data}")
        async with httpx.AsyncClient(
            proxies=config.proxy_url if config.api_use_proxy else None,
            timeout=60,
            ) as client:
            response = await client.post(api, json=data)
            print(response.status_code)
            if response.status_code == 400:
                return [{"type": "string", "string": response.json()["data"]}]
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return [{"type": "string", "string": f"后端服务器连接出错\n{e}\n{data}"}]
    except Exception as e:
        print(e)
        return [{"type": "string", "string": f"出现未知错误\n{e}"}]

async def aget_api(api: str) -> dict:
    """从后端API获取数据

    Args:
        api (str): API地址
        params (dict): 请求参数

    Returns:
        dict: 返回数据
    """
    try:
    # data = json.dumps(data)
        async with httpx.AsyncClient(
            proxies=config.proxy_url if config.api_use_proxy else None,
            timeout=60,
            ) as client:
            response = await client.get(api)
            print(response.status_code)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(e)
        return [{"type": "string", "string": f"后端服务器连接出错\n{e}"}]
    except Exception as e:
        print(e)
        return [{"type": "string", "string": f"出现未知错误\n{e}"}]