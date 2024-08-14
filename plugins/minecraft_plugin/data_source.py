from configs.config import Plugin_Config
from nonebot.log import logger
import traceback

config = Plugin_Config("minecraft_plugin")

if 'group_server' not in config.plugin_content:
    config.plugin_content['group_server'] = {}
    config.update()


def get_group_serverlist(group_id: int):
    """
    说明:
        获取群服务器列表
    参数:
        :param group_id: 群号
    """
    group_id = str(group_id)
    if group_id not in config.plugin_content['group_server']:
        return None
    return config.plugin_content['group_server'][group_id]

def add_group_server(group_id: int, server_name: str, server_address: str, server_type: str = 'java'):
    """
    说明:
        添加群服务器
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
        :param server_address: 服务器地址
    """
    try:
        group_id = str(group_id)
        if group_id not in config.plugin_content['group_server']:
            config.plugin_content['group_server'][group_id] = []
        config.plugin_content['group_server'][group_id].append({
            "name": server_name,
            "address": server_address,
            "type": server_type
        })
        config.update()
        return True
    except Exception as e:
        # logger.error(f"添加服务器失败，错误信息：{e}")
        traceback.print_exc()
        return False
    
def remove_group_server(group_id: int, server_name: str):
    """
    说明:
        移除群服务器
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
    """
    try:
        group_id = str(group_id)
        if group_id not in config.plugin_content['group_server']:
            return
        for server in config.plugin_content['group_server'][group_id]:
            if server_name == server.get('name'):
                config.plugin_content['group_server'][group_id].remove(server)
                config.update()
                return True
    except Exception as e:
        logger.error(f"移除服务器失败，错误信息：{e}")
        return False

def get_server_address(group_id: int, server_name: str):
    """
    说明:
        获取服务器地址
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
    """
    group_id = str(group_id)
    if group_id not in config.plugin_content['group_server']:
        return None
    for server in config.plugin_content['group_server'][group_id]:
        if server_name == server.get('name'):
            return server
    return None
    
def update_server_address(group_id: int, server_name: str, server_address: str):
    """
    说明:
        更新服务器地址
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
        :param server_address: 服务器地址
    """
    try:
        group_id = str(group_id)
        if group_id not in config.plugin_content['group_server']:
            return
        for server in config.plugin_content['group_server'][group_id]:
            if server_name == server.get('name'):
                server['address'] = server_address
                config.update()
                return True
    except Exception as e:
        logger.error(f"更新服务器地址失败，错误信息：{e}")
        return False
    
def update_server_name(group_id: int, server_name: str, new_server_name: str):
    """
    说明:
        更新服务器名称
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
        :param new_server_name: 新的服务器名称
    """
    try:
        group_id = str(group_id)
        if group_id not in config.plugin_content['group_server']:
            return
        for server in config.plugin_content['group_server'][group_id]:
            if server_name == server.get('name'):
                server['name'] = new_server_name
                config.update()
                return True
    except Exception as e:
        logger.error(f"更新服务器名称失败，错误信息：{e}")
        return False