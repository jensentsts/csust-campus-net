# coding=utf-8
import json
import os
import re

import requests

from ccn_instructions import info, failed, success, panel, rule
from ccn_user import User, load_users_data, user_data_path
from wifi_actions import get_networks_data, get_interfaces_data, disconnect, connect

# 设置
settings = json.load(open('./ccn_settings.json', 'r+'))

# 网络信息
wlan_info = {
    'userip': str(),
    'acname': str(),
    'acip': str(),
    'usermac': str(),
}


def is_network_ok(success_info=False) -> bool:

    """获取连接状态"""
    global settings
    try:
        network_test_data = requests.get(url=settings['net']['test']['url'], timeout=settings['net']['timeout']).text
    except requests.RequestException:
        return False
    # 若在测试信息中找到了鉴别内容
    if settings['net']['test']['label'] in network_test_data:
        if success_info:
            success('当前可以正常上网!')
        return True
    return False


def wlan_info_update() -> bool:
    """获取网络信息"""
    global wlan_info
    global settings
    try:
        r = requests.get(url=settings['net']['wlan_info_request_url'], allow_redirects=False, timeout=settings['net']['timeout'])
        wlan_info_url = str(r.headers['Location']).split('&')
    except requests.RequestException:
        return False
    except KeyError as e:
        rule('连接失败')
        failed('网络信息获取失败：可能是您的某些网络设置导致校园网服务器拒绝了您的请求。')
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


def campus_net_post_data(user: User) -> dict:
    """post数据"""
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


def campus_net_post_particular_url(url_label: str, data: dict):
    """向校园网中的特定网址发送post请求"""
    post_url = settings['net'][url_label].format(
        wlanacip=wlan_info['acip'],
        wlanacname=wlan_info['acname'],
        wlanuserip=wlan_info['userip'],
        wlanusermac=wlan_info['usermac'])
    return requests.post(url=post_url, data=data)


def campus_net_logout(user: User):
    """校园网注销"""
    try:
        campus_net_post_particular_url(url_label='logout_url', data=campus_net_post_data(user=user))
    except requests.RequestException:
        failed(f'[yellow]{user.username}', '从校园网', f'[yellow]{user.campus_net_ssid}', '注销失败!')

    else:
        status = is_network_ok()
        if not status:
            success(f'[yellow]{user.username}', '已从校园网', f'[yellow]{user.campus_net_ssid}', '注销.')


def campus_net_login(user: User) -> bool:
    """校园网登录"""
    try:
        request_message = campus_net_post_particular_url(url_label='login_url', data=campus_net_post_data(user=user))
    except requests.RequestException:
        failed('网络错误,', f'[yellow]{user.username}', '无法登录到', f'[yellow]{user.campus_net_ssid}', '!')
        return False
    else:
        login_key_data = request_message.text.split('<title>')[-1].split('</title>')[0]
        if 'aW51c2UsIGxvZ2luIGFnYWlu' in request_message.url:  # 针对 "inuse, login again" 的登录冲突情况
            info(f'[yellow]{user.username}', '在', f'[yellow]{user.campus_net_ssid}', '上重复登陆, 即将注销账号...')

            campus_net_logout(user)
            return campus_net_login(user)  # 长理校园网的注销页面非常管用，绝对不怕爆栈的，而且注销之后的登录一般很管用
        elif '成功' in login_key_data:
            success(f'[yellow]{user.username}', '已成功登陆', f'[yellow]{user.campus_net_ssid}', '!')
            return True
        else:
            failed(f'[yellow]{user.username}', '账号密码错误、不在服务区内或网络抽风, 尝试登录到', f'[yellow]{user.campus_net_ssid}', '失败!')
            return False


def wifi_connect(user: User):
    """wifi连接"""
    info('建立wifi连接...')

    reconnect_try_times = settings['net']['reconnect_try_times']  # 重新连接的次数
    wlan_list = get_networks_data()  # wifi列表
    exist_flag = False  # 判断所处网络环境中是否存在 user.campus_net_ssid 的标记
    for wlan in wlan_list:
        if wlan['SSID'] == user.campus_net_ssid:
            exist_flag = True
    if exist_flag:
        for reconnect_try_times in range(reconnect_try_times, 0, -1):
            interfaces = get_interfaces_data()
            for interface in interfaces:
                wifi_connect_status = False  # wifi连接状态，用于判定和输出是否连接成功的信息
                if interface['SSID'] != user.campus_net_ssid:
                    wifi_connect_status = disconnect() and connect(name=user.campus_net_ssid)
                else:
                    wifi_connect_status = True

                if wifi_connect_status:
                    success('已连接至wifi', f'[yellow]{user.campus_net_ssid}', '!')
                    return
                else:
                    failed(f'[yellow]{user.campus_net_ssid}', '连接失败! 剩余重试次数', f'[yellow]{reconnect_try_times} .')
    else:
        failed(f'[yellow]{user.campus_net_ssid}', '连接失败! 您所处的网络环境中不包含', f'[yellow]{user.campus_net_ssid}')


def user_login(user: User, timeout=settings['net']['timeout']) -> bool:
    """用户登录，包括建立wifi连接和重复尝试登录到校园网"""
    global settings
    info('当前用户:', f'[yellow]{user.username}')
    if settings['log']['show_account_data']:
        panel(f'账号：[yellow]{user.account}[/yellow]\n密码：[yellow]{user.password}[/yellow]',
              title='账户信息')

    # wifi连接
    if settings['net']['auto_connection']:
        wifi_connect(user=user)
    else:
        info('跳过wifi自动连接.')

    for try_times in range(timeout, 0, -1):
        if wlan_info_update():
            success('网络信息获取成功!')
            if settings['log']['show_wlan_info']:
                panel(f'路由器网关地址: {wlan_info["userip"]}\n'
                      f'连接路由器型号: {wlan_info["acname"]}\n'
                      f'用户IP地址: {wlan_info["acip"]}\n'
                      f'路由器MAC地址: {wlan_info["acip"]}',
                      title='网络信息')
            break
        else:
            failed(f'网络信息获取失败! 剩余重试次数 {try_times} .')

    # 登录尝试
    for try_times in range(timeout, 0, -1):
        if is_network_ok(success_info=True):
            return True
        info(f'正在尝试登录', '[yellow]{user.campus_net_ssid}', ', 剩余重试次数 {try_times}...')
        if campus_net_login(user):
            return True
    return False


def login() -> bool:
    """登录到网络"""
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
        failed('请在', f'[yellow]{user_data_path}', '中添加用户信息.')
        os.startfile(user_data_path)  # 打开数据文件
        return is_network_ok(success_info=True)
