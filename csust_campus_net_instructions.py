# coding=utf-8

from rich.text import Text
from rich.console import Console
from csust_campus_net_user import user_data_path


console = Console()


def _make_text(values):
    text = str()
    for v in values:
        text += v
        text += ' '
    return text


def rule(title: str | Text = ''):
    """分割线。"""
    console.rule(title=title)


def _log(text: str, values):
    console.log(f'{text}: {_make_text(values)}')


def info(*values: object):
    """提示信息"""
    _log('INFO', values)


def success(*values: object):
    """成功信息"""
    _log('[green]SUCCESS', values)


def warning(*values: object):
    """警告信息"""
    _log('[yellow]WARNING', values)


def failed(*values: object):
    """失败信息"""
    _log('[red]FAILED', values)


def instructions():
    """项目说明"""
    warning('使用前请先暂时断开VPN，否则很可能无法登录校园网；若登录始终失败多系上次关机前未断开VPN连接，请打开梯子并重新关闭其连接功能。成功登录后可继续正常使用.')
    warning(f'可在文件 {user_data_path} 中编辑用户信息')
    info('遵从开源协议: CC4.0 BY-NC-SA')
    info('本项目基于', '[blue]https://github.com/linfangzhi/CSUST_network_auto_login/tree/master', '二次开发')
    info('本项目在Github上开源，请访问', '[blue]https://github.com/jensentsts/csust-campus-net')
