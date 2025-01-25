# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:35
# @Author  : jensentsts
# @File    : main.py
# @Description :

import argparse
import sys
import time


from core import *

try:
    ccn_core: Core = Core()
except (FileExistsError, FileNotFoundError) as e:
    print(f'{e}')
    print(f'重要文件缺失。')
    exit(0)
except (AddressDataGetError, AddressDataTimeoutError) as e:
    print(f'{e}')
    print(f'获取地址信息出错，也无法读取旧有存储记录。')
    exit(0)


def arg_parse():
    parser = argparse.ArgumentParser(prog=f'CCN',
                                     description=f'{ccn_core.settings["title"]} v{CCN_VERSION}',
                                     epilog='请点击 https://github.com/jensentsts/csust-campus-ne 获得帮助或开源代码')

    parser.add_argument('-k', '-K', '--keep',
                        action='store_true', help='持续重复')
    parser.add_argument('-u', '-U', '--user',
                        type=int,  metavar=str(ccn_core.settings['user']['default']), help='指定用户')

    group = parser.add_argument_group('可选的操作（互斥）')
    group = group.add_mutually_exclusive_group()

    group.add_argument('-v', '-V', '--version',
                       action='store_true', help='查看版本号')
    group.add_argument('-li', '--login',
                       action='store_true', help='登录')
    group.add_argument('-lo', '--logout',
                       action='store_true', help='退出')
    group.add_argument('-a', '-A', '--add',
                       action='store_true', help='添加用户')  # 暂不设
    group.add_argument('-r', '-R', '--remove',
                       action='store_true', help='删除用户')  # 暂不设
    group.add_argument('-e', '-E', '--edit',
                       action='store_true', help='修改用户数据')  # 暂不设
    group.add_argument('-c', '-C', '--check',
                       action='store_true', help='查询用户数据')
    group.add_argument('-l', '-L', '--list',
                       action='store_true', help='查询所有用户数据')

    return parser.parse_args()


if __name__ == '__main__':
    u: int = ccn_core.settings['user']['default']

    if len(sys.argv) <= 1:
        while True:
            if not ccn_core.net_statue_test():
                print(f'网络不可用，请求登录 {ccn_core.get_users()[u]}')
                ccn_core.login(u)
                if not ccn_core.ccn.statue:
                    print(f'{ccn_core.get_users()[u]} 请求登录失败，正在重试。')
                    continue
                else:
                    print(f'{ccn_core.get_users()[u]} 请求登录成功。')
            else:
                print(f'可正常访问网络。')
            time.sleep(ccn_core.settings['keep_mode']['delay'])

    args: argparse.Namespace = arg_parse()

    if args.version:
        print(f'{ccn_core.settings["title"]} v{CCN_VERSION}')

    if args.user is not None:
        u = int(args.user)
    else:
        u = ccn_core.settings['user']['default']

    if args.login:
        ccn_core.login(u)
        if not ccn_core.ccn.statue:
            print(f'{ccn_core.get_users()[u]} 请求登录失败。')
        else:
            print(f'{ccn_core.get_users()[u]} 请求登录成功。')
        while args.keep:
            if not ccn_core.net_statue_test():
                print(f'网络不可用，请求登录 {ccn_core.get_users()[u]}')
                ccn_core.login(u)
                if not ccn_core.ccn.statue:
                    print(f'{ccn_core.get_users()[u]} 请求登录失败，正在重试。')
                    continue
                else:
                    print(f'{ccn_core.get_users()[u]} 请求登录成功。')
            else:
                print(f'可正常访问网络。')
            time.sleep(ccn_core.settings['keep_mode']['delay'])

    if args.logout:
        ccn_core.logout(u)
        print(f'{ccn_core.get_users()[u]} 已退出。')
        while args.keep:
            if not ccn_core.net_statue_test():
                ccn_core.logout(u)
                print(f'{ccn_core.get_users()[u]} 已退出。')
            time.sleep(ccn_core.settings['keep_mode']['delay'])

    if args.check:
        print(ccn_core.get_users()[u].get_dict())

    if args.list:
        for i in ccn_core.get_users():
            print(i.get_dict())
