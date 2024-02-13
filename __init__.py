# coding=utf-8
from ccn_instructions import *
from ccn_auto_login import *
from colorama import Fore

# 启动!
if __name__ == '__main__':
    instructions()
    while True:
        # 自动登录
        for try_times in range(settings['net']['timeout'], 0, -1):
            if login():
                break
            else:
                info(f'登录失败，尝试重新登录. 剩余重试次数 {try_times} .')
    # input('按回车退出. ')
    exit(0)
