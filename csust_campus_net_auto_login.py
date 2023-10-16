import time
import requests
import re
import pywifi
import sys
from tqdm import tqdm
from colorama import Fore, init
from csust_campus_net_user import *
from csust_campus_net_instructions import instructions

# todo: 删减不必要的 sys.stdout.flush()

# 设置
test_url = 'https://www.baidu.com/'  # 测试网络连接状态的url
test_label = 'About Baidu'  # 对url get, 如果请求信息中包含了 test_label 中的内容, 则认为网络连接正常
test_delay = 30  # 检测网络状态延迟（秒）
show_wlan_info = True  # 显示设备信息
show_account = False  # 登录时显示账号
show_password = False  # 登录时显示密码

# 全局变量
# 网络信息
wlanuserip = ''
wlanacname = ''
wlanacip = ''
wlanusermac = ''


# 获取连接状态
def is_network_ok(info=False) -> bool:
    try:
        network_test_data = requests.get(url=test_url, timeout=3).text
    except:
        return False
    else:
        if test_label in network_test_data:
            if info:
                print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                      Fore.RESET + '当前可以正常上网!')
                sys.stdout.flush()
            return True
        return False


# 自动连接到用户对应的wifi
def wifi_connection_control(user: User, timeout=3):
    # 连接到user对应的wifi
    def wifi_connect(ssid: str, ifa: pywifi.wifi.Interface):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = pywifi.const.AUTH_ALG_OPEN
        profile.akm.append(pywifi.const.AKM_TYPE_NONE)

        ifa.disconnect()
        tmp_profile = ifa.add_network_profile(profile)
        ifa.connect(tmp_profile)

        time.sleep(5)

    for try_times in range(timeout, 0, -1):
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        wifi_connect(ssid=user.campus_net_ssid, ifa=iface)  # TODO: 这里直接重新连接一下wifi, 暂时不想再折腾ssid判断的问题了
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.RESET + '已连接至wifi',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '!')
            sys.stdout.flush()
            return True
        else:
            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.RESET + f'尝试重新连接到 {user.campus_net_ssid} ,剩余尝试次数 {try_times} .')
            sys.stdout.flush()
    print(Fore.LIGHTRED_EX + 'FAILED:',
          Fore.RESET + f'连接至wifi {user.campus_net_ssid} 失败.')
    sys.stdout.flush()
    return False


# 获取网络信息
def wlan_info_update():
    wlan_info_request_url = 'http://1.1.1.1/?isReback=1'
    global wlanuserip
    global wlanacname
    global wlanacip
    global wlanusermac
    try:
        print(Fore.LIGHTWHITE_EX + 'INFO:',
              Fore.RESET + '获取网络信息中...')
        sys.stdout.flush()
        wlan_info_url = str(requests.get(url=wlan_info_request_url, allow_redirects=False, timeout=5).headers['Location']).split('&')
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
        print(Fore.LIGHTGREEN_EX + 'SUCCESS:', Fore.RESET + '网络信息获取成功!')
        if show_wlan_info:
            print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'路由器网关地址: {wlanuserip}')
            print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'连接路由器型号: {wlanacname}')
            print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'用户IP地址: {wlanacip}')
            print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'路由器MAC地址: {wlanacip}')
        sys.stdout.flush()
    except:
        print(Fore.LIGHTRED_EX + 'FAILED:',
              Fore.RESET + '网络信息获取失败!')
        sys.stdout.flush()


# post data
def campus_net_post_data(user: User):
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
        request_message = requests.post(url=post_url, data=campus_net_post_data(user))
        status = is_network_ok()
        if not status:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '已从校园网',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '注销.')
            sys.stdout.flush()
        else:
            pass  # TODO: 是否有无法退出的情况
    except:
        print(Fore.LIGHTRED_EX + 'FAILED:',
              Fore.LIGHTYELLOW_EX + f'{user.username}',
              Fore.RESET + '从校园网',
              Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
              Fore.RESET + '注销失败!')
        sys.stdout.flush()
        return None
    else:
        return request_message


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
            login_key_data = 'inuse'
        if '成功' in login_key_data:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '已成功登陆',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '!')
            sys.stdout.flush()
            return True
        elif 'inuse' in login_key_data:
            print(Fore.LIGHTRED_EX + 'FAILED:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '尝试登录到',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '失败!')
            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.RESET + '可能是重复登录导致此问题，尝试排除...')
            sys.stdout.flush()
            campus_net_logout(user)
            return False
        else:
            print(Fore.LIGHTRED_EX + 'FAILED:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '尝试登录到',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '失败!')
            return False


# 用户登录
def user_login(user: User, timeout=5) -> bool:
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
    wifi_connection_control(user)
    for try_times in range(timeout, 0, -1):
        if is_network_ok(info=True):
            return True
        else:
            wlan_info_update()
        print(Fore.LIGHTWHITE_EX + 'INFO:',
              Fore.RESET + f'正在尝试登录 {user.campus_net_ssid} ,剩余次数 {try_times}...')
        sys.stdout.flush()
        if campus_net_login(user):
            return True
    return False


def login():
    users = load_users_data(path=user_data_path)
    if len(users) == 0:
        print(Fore.LIGHTRED_EX + 'ERR:',
              Fore.RESET + '请在',
              Fore.LIGHTYELLOW_EX + user_data_path,
              Fore.RESET + '中添加用户信息.')
        sys.stdout.flush()
        is_network_ok(info=True)
    else:
        for user_data in users:
            if is_network_ok(info=True):
                break
            if not user_login(user=user_data):
                continue
            break


# 启动!
if __name__ == '__main__':
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '连接到校园网前请先暂时关闭包括但不限于VPN等会修改网络配置的软件，否则将连接失败.')
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '可在文件',
          Fore.LIGHTYELLOW_EX + user_data_path,
          Fore.RESET + '中编辑用户信息.')
    sys.stdout.flush()
    init(autoreset=True)
    keep_inspecting = False
    while True:
        login()
        instructions()
        if keep_inspecting or input(
                Fore.LIGHTWHITE_EX + 'INFO:' + Fore.RESET + ' 是否持续检测网络连接状态? (y or any): ').lower() == 'y':
            keep_inspecting = True
            while True:
                proc_bar = tqdm(range(test_delay), desc=Fore.LIGHTWHITE_EX + 'INFO:' + Fore.RESET + ' 距下一次网络检测',
                                unit='meow', leave=False, file=sys.stdout)
                for i in proc_bar:
                    time.sleep(1)
                if not is_network_ok(info=True):
                    break
            print(Fore.LIGHTRED_EX + 'ERR:',
                  Fore.RESET + '网络连接异常!')
            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.RESET + '即将重新连接网络.')
            sys.stdout.flush()
        else:
            break

    input('按回车退出. ')
    exit(0)
