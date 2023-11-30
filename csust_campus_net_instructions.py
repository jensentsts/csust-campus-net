# coding=utf-8
from colorama import Fore
from csust_campus_net_user import user_data_path
import sys


def _make_text(values):
    text = str()
    for v in values:
        text += v
        text += ' '
    return text


# 提示信息
def info(*values: object):
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + _make_text(values))
    sys.stdout.flush()


# 成功信息
def success(*values: object):
    print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
          Fore.RESET + _make_text(values))
    sys.stdout.flush()


# 警告信息
def warning(*values: object):
    print(Fore.LIGHTYELLOW_EX + 'WARNING:',
          Fore.RESET + _make_text(values))
    sys.stdout.flush()


# 失败信息
def failed(*values: object):
    print(Fore.LIGHTRED_EX + 'FAILED:',
          Fore.RESET + _make_text(values))
    sys.stdout.flush()


# 项目说明
def instructions():
    warning(
        '使用前请先暂时断开VPN，否则很可能无法登录校园网；若登录始终失败多系上次关机前未断开VPN连接，请打开梯子并重新关闭其连接功能。成功登录后可继续正常使用.')
    warning('可在文件',
            Fore.LIGHTYELLOW_EX + user_data_path,
            Fore.RESET + '中编辑用户信息.')
    info('遵从开源协议: CC4.0 BY-NC-SA')
    info('本项目基于',
         Fore.LIGHTBLUE_EX + 'https://github.com/linfangzhi/CSUST_network_auto_login/tree/master',
         Fore.RESET + '二次开发')
    info('本项目在Github上开源，请访问',
         Fore.LIGHTBLUE_EX + 'https://github.com/jensentsts/csust-campus-net')
