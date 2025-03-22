from nonebot.plugin import PluginMetadata
from nonebot.plugin import require
require("nonebot_plugin_localstore")
require("nonebot_plugin_uninfo")
from .conf import *
from .resources import *
from .suggar import *
from .API import *
from .conf import __KERNEL_VERSION__


__plugin_meta__ = PluginMetadata(
    name="SuggarChat 高可扩展性大模型聊天插件/框架",
    description="强大的聊天插件/框架，内建OpenAI协议客户端实现，高可扩展性，多模型切换，事件API提供，完全的上下文支持，适配Nonebot2-Onebot-V11适配器",
    usage="https://github.com/JohnRichard4096/nonebot_plugin_suggarchat/wiki",
    homepage="https://github.com/JohnRichard4096/nonebot_plugin_suggarchat/",
    type="application",
    supported_adapters={"~onebot.v11"},
)
