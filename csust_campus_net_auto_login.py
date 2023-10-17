import re
import sys
import time

import pywifi
import requests
from colorama import Fore, init
from tqdm import tqdm

from csust_campus_net_instructions import instructions
from csust_campus_net_user import *

# todo: 删减不必要的 sys.stdout.flush()

# 设置
test_url = 'https://www.baidu.com/'  # 测试网络连接状态的url
test_label = 'About Baidu'  # 对url get, 如果请求信息中包含了 test_label 中的内容, 则认为网络连接正常
test_delay = 30  # 检测网络状态延迟（秒）
show_wlan_info = False  # 显示设备信息
show_account = False  # 登录时显示账号
show_password = False  # 登录时显示密码
network_check_successful_log = False  # 检测网络状况正常时输出“日志”

# 全局变量
# 网络信息
wlanuserip = ''
wlanacname = ''
wlanacip = ''
wlanusermac = ''


# 获取连接状态
def is_network_ok(info=False) -> bool:
    global test_url
    global test_label
    try:
        network_test_data = requests.get(url=test_url, timeout=3).text
    except:
        return False
    if test_label in network_test_data:
        if info:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.RESET + '当前可以正常上网!')
            sys.stdout.flush()
        return True
    return False


# 自动连接到用户对应的wifi
def wifi_connection_control(user: User, timeout=3) -> bool:
    # 连接到user对应的wifi
    def wifi_connect_ssid(ssid: str, ifa: pywifi.wifi.Interface):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = pywifi.const.AUTH_ALG_OPEN
        profile.akm.append(pywifi.const.AKM_TYPE_NONE)

        ifa.disconnect()
        tmp_profile = ifa.add_network_profile(profile)
        ifa.connect(tmp_profile)
        time.sleep(3)

    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    wifi_connect_ssid(ssid=user.campus_net_ssid, ifa=iface)  # TODO: 这里直接重新连接一下wifi, 暂时不想再折腾ssid判断的问题了
    if iface.status() == pywifi.const.IFACE_CONNECTED:
        return True
    return False


# 获取网络信息
def wlan_info_update() -> bool:
    global wlanuserip
    global wlanacname
    global wlanacip
    global wlanusermac
    wlan_info_request_url = 'http://1.1.1.1/?isReback=1'
    try:
        wlan_info_url = str(
            requests.get(url=wlan_info_request_url, allow_redirects=False, timeout=5).headers['Location']).split('&')
    except:
        return False
    for wlan_info_expression in wlan_info_url:
        if 'wlanuserip' in wlan_info_expression:
            wlanuserip = wlan_info_expression.split('=')[-1]
        if 'wlanacip' in wlan_info_expression:
            wlanacip = wlan_info_expression.split('=')[-1]
        if 'wlanacname' in wlan_info_expression:
            wlanacname = wlan_info_expression.split('=')[-1]
        if 'wlanusermac' in wlan_info_expression:
            wlanusermac = wlan_info_expression.split('=')[-1][:12]
            wlanusermac = re.findall(r'\w{1,2}', wlanusermac)
            wlanusermac = '-'.join(wlanusermac)
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


# 校园网注销
def campus_net_logout(user: User):
    try:
        post_url = 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Logout&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&port=&hostname=192.168.7.221&iTermType=1&session=&queryACIP=0&mac={wlanusermac}'.format(
            wlanacip=wlanacip, wlanacname=wlanacname, wlanuserip=wlanuserip, wlanusermac=wlanusermac)
        requests.post(url=post_url, data=campus_net_post_data(user))
    except:
        print(Fore.LIGHTRED_EX + 'FAILED:',
              Fore.LIGHTYELLOW_EX + f'{user.username}',
              Fore.RESET + '从校园网',
              Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
              Fore.RESET + '注销失败!')
        sys.stdout.flush()
    else:
        status = is_network_ok()
        if not status:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '已从校园网',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '注销.')
            sys.stdout.flush()


# 校园网登录
def campus_net_login(user: User) -> bool:
    try:
        post_url = 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Login&protocol=http:&hostname=192.168.7.221&iTermType=1&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&mac={wlanusermac}&ip={wlanuserip}&enAdvert=0&queryACIP=0&loginMethod=1'.format(
            wlanusermac=wlanusermac, wlanacip=wlanacip, wlanacname=wlanacname, wlanuserip=wlanuserip)
        request_message = requests.post(url=post_url, data=campus_net_post_data(user), allow_redirects=True)
    except:
        print(Fore.LIGHTRED_EX + 'ERR:',
              Fore.RESET + '网络错误,',
              Fore.LIGHTYELLOW_EX + f'{user.username}',
              Fore.RESET + '无法登录到',
              Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
              Fore.RESET + '!')
        sys.stdout.flush()
    else:
        login_key_data = request_message.text.split('<title>')[-1].split('</title>')[0]
        if 'aW51c2UsIGxvZ2luIGFnYWlu' in request_message.url:  # 针对 "inuse, login again" 的登录冲突情况
            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '在',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '上重复登陆, 即将注销账号...')
            sys.stdout.flush()
            campus_net_logout(user)
            return campus_net_login(user)  # 长理校园网的注销页面非常管用，绝对不怕爆栈的，而且注销之后的登录一般很管用
        elif '成功' in login_key_data:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '已成功登陆',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '!')
            sys.stdout.flush()
            return True
        else:
            print(Fore.LIGHTRED_EX + 'FAILED:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '账号密码错误、不在服务区内或网络抽风, 尝试登录到',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '失败!')
            return False


# 用户登录，包括建立wifi连接和重复尝试登录到校园网
def user_login(user: User, timeout=5) -> bool:
    global show_wlan_info
    global show_account
    global show_password
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '当前用户:',
          Fore.LIGHTYELLOW_EX + f'{user.username}')
    if show_account:
        print(Fore.LIGHTCYAN_EX + 'DATA:',
              Fore.RESET + '账号:',
              Fore.LIGHTYELLOW_EX + f'{user.account}')
    if show_password:
        print(Fore.LIGHTCYAN_EX + 'DATA:',
              Fore.RESET + '密码:',
              Fore.LIGHTYELLOW_EX + f'{user.password}')
    sys.stdout.flush()
    # wifi连接
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '建立wifi连接...')
    sys.stdout.flush()
    for try_times in range(timeout, 0, -1):
        if wifi_connection_control(user):
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.RESET + '已连接至wifi',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '!')
            sys.stdout.flush()
            break
        else:
            print(Fore.LIGHTWHITE_EX + 'FAILED:',
                  Fore.RESET + f'{user.campus_net_ssid} 连接失败! 剩余重试次数 {try_times} .')
            sys.stdout.flush()
    # 网络信息获取
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '获取网络信息中...')
    sys.stdout.flush()
    for try_times in range(timeout, 0, -1):
        if wlan_info_update():
            if show_wlan_info:
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'路由器网关地址: {wlanuserip}')
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'连接路由器型号: {wlanacname}')
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'用户IP地址: {wlanacip}')
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'路由器MAC地址: {wlanacip}')
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.RESET + '网络信息获取成功!')
            sys.stdout.flush()
            break
        else:
            print(Fore.LIGHTRED_EX + 'FAILED:',
                  Fore.RESET + f'网络信息获取失败! 剩余重试次数 {try_times} .')
            sys.stdout.flush()
    for try_times in range(timeout, 0, -1):
        if is_network_ok(info=True):
            return True
        print(Fore.LIGHTWHITE_EX + 'INFO:',
              Fore.RESET + f'正在尝试登录 {user.campus_net_ssid} , 剩余重试次数 {try_times}...')
        sys.stdout.flush()
        if campus_net_login(user):
            return True
    return False


def login() -> bool:
    users = load_users_data(path=user_data_path)
    if len(users) == 0:
        print(Fore.LIGHTRED_EX + 'ERR:',
              Fore.RESET + '请在',
              Fore.LIGHTYELLOW_EX + user_data_path,
              Fore.RESET + '中添加用户信息.')
        sys.stdout.flush()
        return is_network_ok(info=True)
    else:
        for user_data in users:
            # 检查网络，状况良好则直接结束。
            # 此处调用是为了解决以下问题：
            # 1. 避免同一设备在校园网服务端重复登陆，从而减少不必要的时间浪费
            # 2. 从登陆完成到建立网络连接的延迟问题
            if is_network_ok(info=True):
                return True
            if not user_login(user=user_data):
                continue
            return True
        return False


# 启动!
if __name__ == '__main__':
    init(autoreset=True)
    print(Fore.LIGHTYELLOW_EX + 'WARNING:',
          Fore.RESET + '使用前请先暂时断开VPN，否则很可能无法登录校园网；若登录始终失败多系上次关机前未断开VPN连接，请打开梯子并重新关闭其连接功能。成功登录后可继续正常使用.')
    print(Fore.LIGHTYELLOW_EX + 'WARNING:',
          Fore.RESET + '可在文件',
          Fore.LIGHTYELLOW_EX + sys.path[0] + user_data_path[1:-1],
          Fore.RESET + '中编辑用户信息.')
    sys.stdout.flush()
    keep_inspecting = False  # 是否要持续监测网络连接状态
    while True:
        # 自动登录
        while not login():
            if 'y' in input(
                    Fore.LIGHTWHITE_EX + 'INFO:' + Fore.RESET + ' 网络连接失败，是否尝试重新连接? (y or any): ').lower():
                continue  # 重新login
            break  # 退出
        instructions()
        # 检测网络状态
        if keep_inspecting or 'y' in input(
                Fore.LIGHTWHITE_EX + 'INFO:' + Fore.RESET + ' 是否持续检测网络连接状态? (y or any): ').lower():
            keep_inspecting = True
            while True:
                proc_bar = tqdm(range(test_delay), desc=Fore.LIGHTWHITE_EX + 'INFO:' + Fore.RESET + ' 距下一次网络检测',
                                unit='meow', leave=False, file=sys.stdout)
                for i in proc_bar:
                    time.sleep(1)
                if not is_network_ok(info=network_check_successful_log):
                    print(Fore.LIGHTRED_EX + 'ERR:',
                          Fore.RESET + '网络连接异常!')
                    print(Fore.LIGHTWHITE_EX + 'INFO:',
                          Fore.RESET + '即将重新连接网络.')
                    sys.stdout.flush()
                    break
        else:
            break
    # input('按回车退出. ')
    exit(0)
