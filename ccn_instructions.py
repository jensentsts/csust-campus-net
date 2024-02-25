# coding=utf-8
from rich.panel import Panel
from rich.text import Text
from rich.console import Console, ConsoleRenderable, RichCast
from ccn_user import user_data_path


__console = Console()


def rule(title: str | Text = ''):
    """分割线。"""
    __console.rule(title=title)


def info(*values: object):
    """提示信息"""
    __console.log('INFO:', *values)


def success(*values: object):
    """成功信息"""
    __console.log('[green]SUCCESS:', *values)


def warning(*values: object):
    """警告信息"""
    __console.log('[yellow]WARNING:', *values)


def failed(*values: object):
    """失败信息"""
    __console.log('[red]FAILED:', *values)


def panel(content: ConsoleRenderable | RichCast | str, title: str = ''):
    """面板"""
    __console.print(Panel(content, title=title))


def instructions():
    """项目说明"""
    rule('长沙理工大学校园网登录')
    warning('使用前请先暂时断开VPN，否则很可能无法登录校园网；若登录始终失败多系上次关机前未断开VPN连接，请打开梯子并重新关闭其连接功能。成功登录后可继续正常使用.')
    warning('可在文件', f'[yellow]{user_data_path}', '中编辑用户信息')
    info('遵从开源协议: CC4.0 BY-NC-SA')
    info('本项目基于', '[blue]https://github.com/linfangzhi/CSUST_network_auto_login/tree/master', '二次开发')
    info('本项目在Github上开源，请访问', '[blue]https://github.com/jensentsts/csust-campus-net')
