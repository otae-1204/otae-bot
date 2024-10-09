from utils.plugin_data import Plugin_Data
import traceback

pl_data = Plugin_Data("minecraft_plugin")

# 如果Json文件中没有group_server字段则创建
if pl_data.plugin_data.get('group_server') is None:
    pl_data.plugin_data['group_server'] = {}
    pl_data.save_plugin_data()

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

        # 如果群号不存在则创建
        if group_id not in pl_data.plugin_data['group_server']:
            pl_data.plugin_data['group_server'][group_id] = []

        # 添加服务器
        pl_data.plugin_data['group_server'][group_id].append({
            "name": server_name,
            "address": server_address,
            "type": server_type
        })
        pl_data.save_plugin_data()
        return True
    except Exception as e:
        traceback.print_exc()
        return False

def add_server_nickname(group_id: int, server_name: str, server_nick: str):
    """
    说明:
        添加服务器昵称
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
        :param server_nick: 服务器昵称
    """
    try:
        group_id = str(group_id)

        # 如果群号不存在则返回None
        if group_id not in pl_data.plugin_data['group_server']:
            return
        
        # 添加服务器昵称
        for server in pl_data.plugin_data['group_server'][group_id]:
            if server_name == server.get('name'):
                if server.get('nickname') is not None:
                    server['nickname'] = [server_nick]
                else:
                    server['nickname'].append(server_nick)
                pl_data.save_plugin_data()
                return True
    except Exception as e:
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

        # 如果群号不存在则返回None
        if group_id not in pl_data.plugin_data['group_server']:
            return None
        
        # 移除服务器
        for server in pl_data.plugin_data['group_server'][group_id]:
            if server_name == server.get('name'):
                pl_data.plugin_data['group_server'][group_id].remove(server)
                pl_data.save_plugin_data()
                return True
    except Exception as e:
        traceback.print_exc()
        return False

def remove_server_nickname(group_id: int, server_name: str, server_nick: str):
    """
    说明:
        移除服务器昵称
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
        :param server_nick: 要删除的服务器昵称
    """
    try:
        group_id = str(group_id)

        # 如果群号不存在则返回None
        if group_id not in pl_data.plugin_data['group_server']:
            return None
        
        # 移除服务器昵称
        for server in pl_data.plugin_data['group_server'][group_id]:
            if server_name == server.get('name'):
                if server.get('nickname') is not None and server_nick in server.get('nickname'):
                    server['nickname'].remove(server_nick)
                    pl_data.save_plugin_data()
                    return True
                else:
                    return False
    except Exception as e:
        traceback.print_exc()
        return False

def get_group_serverlist(group_id: int):
    """
    说明:
        获取群服务器列表
    参数:
        :param group_id: 群号
    """
    group_id = str(group_id)
    if group_id not in pl_data.plugin_data['group_server']:
        return None
    return pl_data.plugin_data['group_server'][group_id]

def get_server_address(group_id: int, server_name: str):
    """
    说明:
        获取服务器地址
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
    """
    group_id = str(group_id)

    # 如果群号不存在则返回None
    if group_id not in pl_data.plugin_data['group_server']:
        return None
    
    # 获取服务器地址
    for server in pl_data.plugin_data['group_server'][group_id]:
        if server_name == server.get('name'):
            return server
    return None

def get_server_address_by_address(group_id: int, server_address: str):
    """
    说明:
        通过服务器地址获取服务器信息
    参数:
        :param group_id: 群号
        :param server_address: 服务器地址
    """
    group_id = str(group_id)

    # 如果群号不存在则返回None
    if group_id not in pl_data.plugin_data['group_server']:
        return None
    
    # 获取服务器信息
    for server in pl_data.plugin_data['group_server'][group_id]:
        if server_address == server.get('address'):
            return server
    return None

def get_server_address_by_nick(group_id: int, server_nick: str):
    """
    说明:
        通过服务器昵称获取服务器信息
    参数:
        :param group_id: 群号
        :param server_nick: 服务器昵称
    """
    group_id = str(group_id)

    # 如果群号不存在则返回None
    if group_id not in pl_data.plugin_data['group_server']:
        return None
    
    # 获取服务器信息
    for server in pl_data.plugin_data['group_server'][group_id]:
        if server_nick == server.get('nickname'):
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

        # 如果群号不存在则返回None
        if group_id not in pl_data.plugin_data['group_server']:
            return
        
        # 更新服务器地址
        for server in pl_data.plugin_data['group_server'][group_id]:
            if server_name == server.get('name'):
                server['address'] = server_address
                pl_data.save_plugin_data()
                return True
    except Exception as e:
        traceback.print_exc()
        return False

def update_server_name(group_id: int, server_name: str, new_server_name: str):
    """
    说明:
        更新服务器名称
    参数:
        :param group_id: 群号
        :param server_name: 服务器名称
        :param new_server_name: 新服务器名称
    """
    try:
        group_id = str(group_id)

        # 如果群号不存在则返回None
        if group_id not in pl_data.plugin_data['group_server']:
            return False
        
        # 更新服务器名称
        for server in pl_data.plugin_data['group_server'][group_id]:
            if server_name == server.get('name'):
                server['name'] = new_server_name
                pl_data.save_plugin_data()
                return True
    except Exception as e:
        traceback.print_exc()
        return False