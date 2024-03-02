# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:35
# @Author  : jensentsts
# @File    : main.py
# @Description :
import time

import ccn_assistant
from ccn_assistant import User
import argparse
import sys


VERSION = 'v0.2.1'


def parse_arguments() -> argparse.Namespace:
    """参数解析"""
    # arguments like:
    # -ki
    # or
    # (-a) ([--index] / ([-p] [-w])) ([-i / -o] / [--add / --edit / --remove])
    # optional todo: 使用子解析器简化指令
    parser = argparse.ArgumentParser(prog=f'CCN {VERSION}', description='CCN Assistant Arguments', epilog='To get more help and source opened: visit https://github.com/jensentsts/csust-campus-net')

    parser.add_argument('--keep-inspecting', action='store_true', help='Keep inspecting.')  # optional todo: 可以替换为其它功能
    # 用户
    user_group = parser.add_argument_group('User Arguments')
    user_specification_or_index_group = user_group.add_mutually_exclusive_group(required=False)  # index 或 密码+ssid
    user_specification_or_index_group.add_argument('-a', '--account', type=str, metavar='202101010101', help='Account name.')
    user_specification_or_index_group.add_argument('-i', '--index', type=int, metavar='0', help='Index of an account in users.json')
    user_group.add_argument('-p', '--psw', type=str, metavar='000000', help='Account password.')
    user_wlan_group = user_group.add_mutually_exclusive_group(required=False)
    user_wlan_group.add_argument('-w', '--wlan', type=str, metavar='csust-xx', help='WLAN SSID')
    user_wlan_group.add_argument('-nw', '--no-wlan', action='store_true', help='Given for DO NOT connect to WLAN.')
    # 操作
    action_group = parser.add_argument_group('Action Arguments')
    action_exclusive_group = action_group.add_mutually_exclusive_group(required=False)
    # 网络操作
    action_exclusive_group.add_argument('-kli', '--keep-log-in', action='store_true', help='Keep the specified user logged in.')
    action_exclusive_group.add_argument('-klo', '--keep-log-out', action='store_true', help='Keep the specified user logged out.')
    action_exclusive_group.add_argument('-li', '--log-in', action='store_true', help='Log in.')
    action_exclusive_group.add_argument('-lo', '--log-out', action='store_true', help='Log out.')
    # 用户数据
    action_exclusive_group.add_argument('--add', action='store_true', help='Add as a new user.')
    action_exclusive_group.add_argument('--edit', action='store_true', help='Edit an existing user.')
    action_exclusive_group.add_argument('--remove', action='store_true', help='Remove an existing user.')  # 注：remove会要求输入密码
    action_exclusive_group.add_argument('--check', action='store_true', help='Check users list.')  # 注：remove会要求输入密码  # optional todo: 若使用子解析器优化，此处先占个位子。
    return parser.parse_args()


if __name__ == '__main__':
    assistant = ccn_assistant.CCN_Assistant()
    assistant.load('./users.json')

    if len(sys.argv) <= 1:
        assistant.keep_inspecting()
    else:
        args = parse_arguments()

        if args.keep_inspecting:
            assistant.keep_inspecting()
        # user specification
        if args.index is not None:
            specified_user = args.index
        elif args.account is not None:
            if not args.no_wlan:
                specified_user = User({'account': args.account, 'password': args.psw, 'ccn_ssid': args.wlan})
            else:
                specified_user = User({'account': args.account, 'password': args.psw, 'ccn_ssid': 'csust-xx'})
        else:
            specified_user = None
        # Log in / out
        if args.log_in:
            if assistant.user_login(specified_user, not args.no_wlan):
                print('Success.')
            else:
                print('Failed.')
        if args.log_out:
            if assistant.user_logout(specified_user, not args.no_wlan):
                print('Success.')
            else:
                print('Failed.')
        while args.keep_log_in:  # optional todo: 优化keep系列参数及其执行
            if assistant.user_login(specified_user, not args.no_wlan):
                print('Success.')
                time.sleep(60)
            else:
                print('Failed.')
                time.sleep(3)
        while args.keep_log_out:
            if assistant.user_logout(specified_user, not args.no_wlan):
                print('Success.')
                time.sleep(60)
            else:
                print('Failed.')
                time.sleep(3)
        # About data
        if args.add:
            assistant.add_user(specified_user)
            assistant.list_users()
            assistant.save('./users.json')
        if args.edit:
            assistant.edit_user(specified_user)
            assistant.list_users()
            assistant.save('./users.json')
        if args.remove:
            assistant.remove_user(specified_user)
            assistant.list_users()
            assistant.save('./users.json')
        if args.check:
            assistant.list_users(specified_user)

