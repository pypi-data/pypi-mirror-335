# 施工中。。。。。。敬请期待
from .suggar import send_to_admin, get_chat, reload_from_memory
from . import suggar
import threading
from nonebot import logger
from .resources import get_config, save_config, get_models
from . import resources


class Config:
    """用于处理Config注册的类"""

    def __init__(self):
        """
        初始化 Config 类的新实例。
        """
        pass

    def get_config(self, value: str | None):
        if value == None:
            return get_config()
        else:
            return (get_config())[value]

    def get_models(self):
        return get_models()

    def reg_config(self, key: str):
        if not key in resources.__default_config__:
            resources.__default_config__[key] = None
            get_config()
            reload_from_memory()
        else:
            raise Exception(f"Config key {key} already exists!")

    def reg_model_config(self, key: str):
        if not key in resources.__default_model_conf__:
            resources.__default_model_conf__[key] = None
            get_models()
            reload_from_memory()
        else:
            raise Exception(f"Config key {key} already exists!")


class Adapter:
    """用于处理Adapter注册的类"""

    def __init__(self):
        """
        初始化 Adapter 类的新实例。
        """
        pass

    def register_adapter(self, func: callable, protocol: str):
        """
        注册一个适配器。
        """
        if protocol in suggar.protocols_adapters:
            raise ValueError("协议适配器已存在")
        suggar.protocols_adapters[protocol] = func


class Menu:
    """
    Menu 类用于通过注册菜单项来构建菜单。
    """

    def __init__(self):
        """
        初始化 Menu 类的新实例。
        """
        pass

    def reg_menu(self, cmd_name: str, describe: str):
        """
        注册一个新的菜单项。

        参数:
        - cmd_name (str): 菜单项的命令名称。
        - describe (str): 菜单项的描述。

        返回:
        - Menu: 返回 Menu 类的实例，支持方法链式调用。
        """
        suggar.menu_msg += f"{cmd_name} \n"
        return self


class Admin:
    config: dict
    """
    管理员管理类，负责处理与管理员相关的操作，如发送消息、错误处理和管理员权限管理。
    """

    def __init__(self):
        """
        构造函数
        """
        self.config = get_config()

    async def send_with(self, msg: str):
        """
        异步发送消息给管理员。

        参数:
        - msg (str): 要发送的消息内容。

        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        await send_to_admin(msg)
        return self

    async def send_error(self, msg: str):
        """
        异步发送错误消息给管理员，并记录错误日志。

        参数:
        - msg (str): 要发送的错误消息内容。

        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        logger.error(msg)
        await send_to_admin(msg)
        return self

    def is_admin(self, user_id: int) -> bool:
        config = self.config
        """
        检查用户是否是管理员。
        
        参数:
        - user_id (int): 用户ID。
        
        返回:
        - bool: 用户是否是管理员。
        """
        return user_id in config["admins"]

    def add_admin(self, user_id: int):
        config = self.config
        """
        添加新的管理员用户ID到配置中。
        
        参数:
        - user_id (int): 要添加的用户ID。
        
        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        config["admins"].append(user_id)
        save_config(config)
        self.config = get_config()
        return self

    def set_admin_group(self, group_id: int):
        config = self.config
        """
        设置管理员组ID。
        
        参数:
        - group_id (int): 管理员组ID。
        
        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        config["admin_group"] = group_id
        save_config(config)
        self.config = get_config()
        return self


class Chat:
    config: dict
    """
    Chat 类用于处理与LLM相关操作，如获取消息。
    """

    def __init__(self):
        """
        构造函数
        """
        self.config = get_config()

    async def get_msg(self, prompt: str, message: list):
        message.insert(0, {"role": "assistant", "content": prompt})
        return await get_chat(messages=message)

    async def get_msg_on_list(self, message: list):
        return await get_chat(messages=message)
