# coding=utf-8
import json
import re
import sys
import time
import os

import pywifi
import requests
from colorama import Fore, init
from tqdm import tqdm

from csust_campus_net_instructions import instructions, info, failed, success, warning
from csust_campus_net_user import User, load_users_data, user_data_path

# 设置
settings = json.load(open('./settings.json', 'r+'))

# 网络信息
wlan_info = {
    'userip': str(),
    'acname': str(),
    'acip': str(),
    'usermac': str(),
}


# 获取连接状态
def is_network_ok(success_info=False) -> bool:
    global settings
    try:
        network_test_data = requests.get(url=settings['net']['test']['url'], timeout=settings['net']['timeout']).text
    except requests.RequestException:
        return False
    if settings['net']['test']['label'] in network_test_data:
        if success_info:
            success('当前可以正常上网!')

        return True
    return False


# 获取网络信息
def wlan_info_update() -> bool:
    global wlan_info
    global settings
    try:
        wlan_info_url = str(
            requests.get(url=settings['net']['wlan_info_request_url'], allow_redirects=False,
                         timeout=settings['net']['timeout']).headers['Location']).split('&')
    except requests.RequestException:
        return False
    for wlan_info_expression in wlan_info_url:
        if 'wlanuserip' in wlan_info_expression:
            wlan_info['userip'] = wlan_info_expression.split('=')[-1]
        if 'wlanacip' in wlan_info_expression:
            wlan_info['acip'] = wlan_info_expression.split('=')[-1]
        if 'wlanacname' in wlan_info_expression:
            wlan_info['acname'] = wlan_info_expression.split('=')[-1]
        if 'wlanusermac' in wlan_info_expression:
            wlan_info['usermac'] = wlan_info_expression.split('=')[-1][:12]
            wlan_info['usermac'] = re.findall(r'\w{1,2}', wlan_info['usermac'])
            wlan_info['usermac'] = '-'.join(wlan_info['usermac'])
    return True


# post data
def campus_net_post_data(user: User) -> dict:
    return {
        'DDDDD': ',0,{}'.format(user.account),
        'upass': '{}'.format(user.password),
        'R1': '0',
        'R2': '0',
        'R3': '0',
        'R6': '0',
        'para': '00',
        '0MKKey': '123456',
    }


# 向校园网中的特定网址发送post请求
def campus_net_post_particular_url(url_label: str, data: dict):
    post_url = settings['net'][url_label].format(
        wlanacip=wlan_info['acip'],
        wlanacname=wlan_info['acname'],
        wlanuserip=wlan_info['userip'],
        wlanusermac=wlan_info['usermac'])
    return requests.post(url=post_url, data=data)


# 校园网注销
def campus_net_logout(user: User):
    try:
        campus_net_post_particular_url(url_label='logout_url', data=campus_net_post_data(user=user))
    except requests.RequestException:
        failed(Fore.LIGHTYELLOW_EX + f'{user.username}',
               Fore.RESET + '从校园网',
               Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
               Fore.RESET + '注销失败!')

    else:
        status = is_network_ok()
        if not status:
            success(Fore.LIGHTYELLOW_EX + f'{user.username}',
                    Fore.RESET + '已从校园网',
                    Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                    Fore.RESET + '注销.')


# 校园网登录
def campus_net_login(user: User) -> bool:
    try:
        request_message = campus_net_post_particular_url(url_label='login_url', data=campus_net_post_data(user=user))
    except requests.RequestException:
        failed(Fore.RESET + '网络错误,',
               Fore.LIGHTYELLOW_EX + f'{user.username}',
               Fore.RESET + '无法登录到',
               Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
               Fore.RESET + '!')
    else:
        login_key_data = request_message.text.split('<title>')[-1].split('</title>')[0]
        if 'aW51c2UsIGxvZ2luIGFnYWlu' in request_message.url:  # 针对 "inuse, login again" 的登录冲突情况
            info(Fore.LIGHTYELLOW_EX + f'{user.username}',
                 Fore.RESET + '在',
                 Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                 Fore.RESET + '上重复登陆, 即将注销账号...')

            campus_net_logout(user)
            return campus_net_login(user)  # 长理校园网的注销页面非常管用，绝对不怕爆栈的，而且注销之后的登录一般很管用
        elif '成功' in login_key_data:
            success(Fore.LIGHTYELLOW_EX + f'{user.username}',
                    Fore.RESET + '已成功登陆',
                    Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                    Fore.RESET + '!')

            return True
        else:
            failed(Fore.LIGHTYELLOW_EX + f'{user.username}',
                   Fore.RESET + '账号密码错误、不在服务区内或网络抽风, 尝试登录到',
                   Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                   Fore.RESET + '失败!')
            return False


# 连接到ssid
def wifi_connect_ssid(ssid: str) -> bool:
    wifi = pywifi.PyWiFi()
    ifa = wifi.interfaces()[0]
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    profile.akm.append(pywifi.const.AKM_TYPE_NONE)

    ifa.disconnect()
    tmp_profile = ifa.add_network_profile(profile)
    ifa.connect(tmp_profile)
    time.sleep(3)
    if ifa.status() == pywifi.const.IFACE_CONNECTED:
        return True
    return False


# wifi连接
def wifi_connect(user: User, timeout=settings['net']['timeout']):
    info('建立wifi连接...')

    for try_times in range(timeout, 0, -1):
        if wifi_connect_ssid(ssid=user.campus_net_ssid):
            success('已连接至wifi',
                    Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                    Fore.RESET + '!')

            break
        else:
            failed(f'{user.campus_net_ssid} 连接失败! 剩余重试次数 {try_times} .')


# 用户登录，包括建立wifi连接和重复尝试登录到校园网
def user_login(user: User, timeout=settings['net']['timeout']) -> bool:
    global settings
    info('当前用户:',
         Fore.LIGHTYELLOW_EX + f'{user.username}')
    if settings['log']['show_account']:
        info('账号:',
             Fore.LIGHTYELLOW_EX + f'{user.account}')
    if settings['log']['show_password']:
        info('密码:',
             Fore.LIGHTYELLOW_EX + f'{user.password}')

    # wifi连接
    if settings['net']['auto_connection']:
        wifi_connect(user=user)
    else:
        info('跳过wifi自动连接.')

    # 网络信息获取
    info('获取网络信息中...')

    for try_times in range(timeout, 0, -1):
        if wlan_info_update():
            if settings['log']['show_wlan_info']:
                info(f'路由器网关地址: {wlan_info["userip"]}')
                info(f'连接路由器型号: {wlan_info["acname"]}')
                info(f'用户IP地址: {wlan_info["acip"]}')
                info(f'路由器MAC地址: {wlan_info["acip"]}')
            success('网络信息获取成功!')

            break
        else:
            failed(f'网络信息获取失败! 剩余重试次数 {try_times} .')

    # 登录尝试
    for try_times in range(timeout, 0, -1):
        if is_network_ok(success_info=True):
            return True
        info(f'正在尝试登录 {user.campus_net_ssid} , 剩余重试次数 {try_times}...')

        if campus_net_login(user):
            return True
    return False


def login() -> bool:
    users = load_users_data(path=user_data_path)
    if len(users) != 0:
        for user_data in users:
            # 检查网络，状况良好则直接结束。
            # 此处调用是为了解决以下问题：
            # 1. 避免同一设备在校园网服务端重复登陆，从而减少不必要的时间浪费
            # 2. 从登陆完成到建立网络连接的延迟问题
            if is_network_ok(success_info=True):
                return True
            if not user_login(user=user_data):
                continue
            return True
        return False
    # 缺少用户信息
    else:
        failed('请在',
               Fore.LIGHTYELLOW_EX + user_data_path,
               Fore.RESET + '中添加用户信息.')

        os.startfile(user_data_path)  # 打开文件
        return is_network_ok(success_info=True)
