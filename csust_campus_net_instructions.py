from colorama import Fore
from csust_campus_net_user import *
import sys


# 项目说明
def instructions():
    print(Fore.LIGHTYELLOW_EX + 'WARNING:',
          Fore.RESET + '使用前请先暂时断开VPN，否则很可能无法登录校园网；若登录始终失败多系上次关机前未断开VPN连接，请打开梯子并重新关闭其连接功能。成功登录后可继续正常使用.')
    print(Fore.LIGHTYELLOW_EX + 'WARNING:',
          Fore.RESET + '可在文件',
          Fore.LIGHTYELLOW_EX + user_data_path,
          Fore.RESET + '中编辑用户信息.')
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '遵从开源协议: CC4.0 BY-NC-SA')
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '本项目基于',
          Fore.LIGHTBLUE_EX + 'https://github.com/linfangzhi/CSUST_network_auto_login/tree/master',
          Fore.RESET + '二次开发')
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '本项目开源发布于',
          Fore.LIGHTBLUE_EX + 'https://github.com/jensentsts/csust-campus-net')
    sys.stdout.flush()
