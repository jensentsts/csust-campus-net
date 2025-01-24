# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:35
# @Author  : jensentsts
# @File    : main.py
# @Description :

import argparse
import sys
import time

from core import *


core: Core = Core()


def arg_parse():
    parser = argparse.ArgumentParser(prog=f'CCN {CCN_VERSION}', description='CCN助手参数', epilog='请点击 https://github.com/jensentsts/csust-campus-ne 获得帮助或开源代码')

    parser.add_argument('-k', '--keep', action='store_true', help='持续重复')
    parser.add_argument('-u', '--user', type=int, metavar=str(core.settings['user']['default']), help='持续重复')

    group = parser.add_argument_group('参数列表')
    group = group.add_mutually_exclusive_group()

    group.add_argument('-li', '--login', action='store_true', help='登录')
    group.add_argument('-lo', '--logout', action='store_true', help='退出')
    # group.add_argument('-a', '--add', action='store_true', help='添加用户')  # 暂不设
    # group.add_argument('-r', '--remove', action='store_true', help='删除用户')  # 暂不设
    # group.add_argument('-e', '--edit', action='store_true', help='修改用户数据')  # 暂不设
    group.add_argument('-c', '--check', action='store_true', help='查询用户数据')
    group.add_argument('-v', '-V', '--version', action='store_true', help='查询版本号')

    return parser.parse_args()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        while True:
            if core.net_statue_test():
                time.sleep(core.settings['keep_mode']['delay'])
                continue
            else:
                core.login(core.settings['user']['default'])
                time.sleep(core.settings['keep_mode']['delay'])

    args: argparse.Namespace = arg_parse()
    u: int = core.settings['user']['default']

    if args.version:
        print(f'CCN助手 v{CCN_VERSION}')

    if args.user is not None:
        u = int(args.user)

    if args.login:
        core.login(u)
        while args.keep:
            if core.net_statue_test():
                time.sleep(core.settings['keep_mode']['delay'])
                continue
            else:
                core.login(core.settings['user']['default'])
                time.sleep(core.settings['keep_mode']['delay'])

    if args.logout:
        core.logout(u)
        while args.keep:
            if core.net_statue_test():
                time.sleep(core.settings['keep_mode']['delay'])
                continue
            else:
                core.logout(core.settings['user']['default'])
                time.sleep(core.settings['keep_mode']['delay'])

    if args.check:
        print(core.get_users()[u].get_dict())
