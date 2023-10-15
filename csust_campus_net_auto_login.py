import time
import requests
import re
from colorama import Fore, init
import pywifi
from csust_campus_net_user import *
from tqdm import tqdm
import sys
from csust_campus_net_instructions import instructions


# 设置
test_url = 'https://www.baidu.com/'  # 测试网络连接的url
test_label = 'About Baidu'  # 对url获取内容的辨识字符，如果存在test_label，证明链接成功
test_delay = 10  # 检测网络状态延迟（秒）
show_device_data = False  # 显示设备信息


# 全局变量
wlanuserip = ''
wlanacname = ''
wlanacip = ''
wlanusermac = ''


# 获取连接状态
def is_network_ok() -> bool:
    try:
        network_test_data = requests.get(url=test_url, timeout=3).text
    except:
        return False
    else:
        if test_label in network_test_data:
            return True
        return False


# 检测 wifi 是否连接
def wifi_connect(user: User, iface: pywifi.wifi.Interface):
    profile = pywifi.Profile()
    profile.ssid = user.campus_net_ssid
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    profile.akm.append(pywifi.const.AKM_TYPE_NONE)

    iface.disconnect()
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    iface.connect(tmp_profile)

    time.sleep(3)


# 自动连接到用户对应的wifi
def wifi_judge(user: User, timeout=3):
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + f'判断 {user.campus_net_ssid} 连接状态...')
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    if iface.status() in [pywifi.const.IFACE_CONNECTED, pywifi.const.IFACE_INACTIVE] and iface.scan_results()[0].ssid == user.campus_net_ssid:
        print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
              Fore.RESET + '已连接至',
              Fore.LIGHTYELLOW_EX + f'{iface.scan_results()[0].ssid}',
              Fore.RESET + '!')
        return True
    elif timeout == 0:
        print(Fore.LIGHTRED_EX + 'ERR:',
              Fore.RESET + f'未成功连接至 {user.campus_net_ssid}, 即将重试连接, 剩余重试次数: {timeout - 1}.')
        return False
    else:
        print(Fore.LIGHTWHITE_EX + 'INFO:',
              Fore.RESET + f'检测到未连接至网络.{user.campus_net_ssid} .')
        print(Fore.LIGHTWHITE_EX + 'INFO:',
              Fore.RESET + f'正在尝试连接至 {user.campus_net_ssid} ...')
        wifi_connect(user=user, iface=iface)
        return wifi_judge(user=user, timeout=timeout - 1)


# 校园网登录
def user_login(user: User) -> bool:
    device_url = 'http://1.1.1.1/?isReback=1'
    timeout = 5
    status = is_network_ok()
    if status:
        print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
              Fore.RESET + '当前可以正常上网!')
        return True
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '当前用户名:',
          Fore.LIGHTYELLOW_EX + f'{user.username}',
          Fore.RESET + '.')
    wifi_judge(user)
    while timeout != 0:
        timeout -= 1
        status = is_network_ok()
        if status:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.RESET + '当前可以正常上网!')
            return True
        try:
            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.RESET + f'正在尝试登录 {user.campus_net_ssid} ...')
            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.RESET + '获取相关信息中...')
            device_info_url = str(requests.get(url=device_url, allow_redirects=False, timeout=5).headers['Location'])
            device_info = device_info_url.split('&')
            global wlanuserip
            global wlanacname
            global wlanacip
            global wlanusermac
            for url_args in device_info:
                if 'wlanuserip' in url_args:
                    wlanuserip = url_args.split('=')[-1]
                if 'wlanacip' in url_args:
                    wlanacip = url_args.split('=')[-1]
                if 'wlanacname' in url_args:
                    wlanacname = url_args.split('=')[-1]
                if 'wlanusermac' in url_args:
                    wlanusermac = url_args.split('=')[-1][:12]
                    wlanusermac = re.findall(r'\w{1,2}', wlanusermac)
                    wlanusermac = '-'.join(wlanusermac)
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:', Fore.RESET + '获取成功!')
            if show_device_data:
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'路由器网关地址: {wlanuserip}')
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'连接路由器型号: {wlanacname}')
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'用户IP地址: {wlanacip}')
                print(Fore.LIGHTCYAN_EX + 'DATA:', Fore.RESET + f'路由器MAC地址: {wlanacip}')

            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.RESET + '开始尝试登陆...')
            post_url = 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Login&protocol=http:&hostname=192.168.7.221&iTermType=1&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&mac={wlanusermac}&ip={wlanuserip}&enAdvert=0&queryACIP=0&loginMethod=1'.format(
                wlanusermac=wlanusermac, wlanacip=wlanacip, wlanacname=wlanacname, wlanuserip=wlanuserip)
            login_data = {
                'DDDDD': ',0,{}'.format(user.account),
                'upass': '{}'.format(user.password),
                'R1': '0',
                'R2': '0',
                'R3': '0',
                'R6': '0',
                'para': '00',
                '0MKKey': '123456',
            }
            login_request_message = requests.post(url=post_url, data=login_data, allow_redirects=True)
        except:
            print(Fore.LIGHTRED_EX + 'ERR:',
                  Fore.RESET + '网络错误,',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '无法登录到',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                  Fore.RESET + '!')
        else:
            login_key_data = login_request_message.text.split('<title>')[-1].split('</title>')[0]
            if 'aW51c2UsIGxvZ2luIGFnYWlu' in login_request_message.url:
                login_key_data += 'inuse'
            if '成功' in login_key_data:
                print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                      Fore.LIGHTYELLOW_EX + f'{user.username}',
                      Fore.RESET + '已成功登陆',
                      Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                      Fore.RESET + '!')
                return True
            elif 'AC' in login_key_data or 'inuse' in login_key_data:
                print(Fore.LIGHTRED_EX + 'ERR:',
                      Fore.LIGHTYELLOW_EX + f'{user.username}',
                      Fore.RESET + '尝试登录到',
                      Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                      Fore.RESET + '失败!')
                print(Fore.LIGHTWHITE_EX + 'INFO:',
                      Fore.RESET + '可能是重复登录导致此问题，尝试排除...')
                user_logout(user)
            elif '信息页' in login_key_data and 'inuse' not in login_key_data:
                print(Fore.LIGHTRED_EX + 'ERR:',
                      Fore.LIGHTYELLOW_EX + f'{user.username}',
                      Fore.RESET + '的账号或密码错误, 登录到',
                      Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}',
                      Fore.RESET + '失败!')
                return False
    return False


def user_logout(user):
    try:
        post_url = 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Logout&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&port=&hostname=192.168.7.221&iTermType=1&session=&queryACIP=0&mac={wlanusermac}'.format(
            wlanacip=wlanacip, wlanacname=wlanacname, wlanuserip=wlanuserip, wlanusermac=wlanusermac)
        logout_data = {
            'DDDDD': ',0,{}'.format(user.account),
            'upass': '{}'.format(user.password),
            'R1': '0',
            'R2': '0',
            'R3': '0',
            'R6': '0',
            'para': '00',
            '0MKKey': '123456',
        }
        requests.post(url=post_url, data=logout_data)
        status = is_network_ok()
        if not status:
            print(Fore.LIGHTGREEN_EX + 'SUCCESS:',
                  Fore.LIGHTYELLOW_EX + f'{user.username}',
                  Fore.RESET + '已退出',
                  Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}', Fore.RESET + '.')
    except:
        print(Fore.LIGHTRED_EX + 'ERR:',
              Fore.LIGHTYELLOW_EX + f'{user.username}',
              Fore.RESET + '尝试退出',
              Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}', Fore.RESET + '失败!')




def login():
    users = load_users_data(path=users_file_path)
    if len(users) == 0:
        print(Fore.LIGHTRED_EX + 'ERR:',
              Fore.RESET + '但你没有任何用户信息!')
    else:
        for user_data in users:
            res = user_login(user=user_data)
            if res:
                break


# 启动!
if __name__ == '__main__':
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '连接到校园网前请先暂时关闭包括但不限于VPN等会修改网络配置的软件，否则将连接失败.')
    print(Fore.LIGHTWHITE_EX + 'INFO:',
          Fore.RESET + '可以使用',
          Fore.LIGHTYELLOW_EX + 'csust_campus_net_user_editor',
          Fore.RESET + '编辑用户信息.')
    init(autoreset=True)
    keep_inspecting = False
    while True:
        login()
        instructions()
        if keep_inspecting or input(Fore.LIGHTWHITE_EX + 'INFO:' + Fore.RESET + ' 是否持续检测网络连接状态? (y or any): ').lower() == 'y':
            keep_inspecting = True
            while True:
                proc_bar = tqdm(range(test_delay), desc=Fore.LIGHTWHITE_EX + 'INFO:' + Fore.RESET + ' 距下一次网络检测', unit='meow', leave=False, file=sys.stdout)
                for i in proc_bar:
                    time.sleep(1)
                if is_network_ok():
                    print(Fore.LIGHTWHITE_EX + 'INFO:',
                          Fore.RESET + '网络连接正常.')
                else:
                    break
            print(Fore.LIGHTRED_EX + 'ERR:',
                  Fore.RESET + '网络连接异常!')
            print(Fore.LIGHTWHITE_EX + 'INFO:',
                  Fore.RESET + '即将重新连接网络.')
        else:
            break

    input('按回车退出. ')
    exit(0)
