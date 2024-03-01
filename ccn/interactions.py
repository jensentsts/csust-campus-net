# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:58
# @Author  : jensentsts
# @File    : ccn_interactions.py.py
# @Description : 与长理校园网进行交互
import json
import re

from .action import ActionBase, ActionLog, ActionWifi
from wifi_actions import (get_networks_data, get_interfaces_data, connect, disconnect)
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "",
}


class Interactions:
    # __WLAN_INFO_REQUEST_URL: str = 'http://1.1.1.1/?isReback=1'  # get 以用于获取网络信息 较旧的网址 仍然可用 - 注释于 ->> 2024.03.01 19:57 <<-
    __WLAN_INFO_REQUEST_URL: str = 'http://gstatic.com/'  # get 以用于获取网络信息 较新的网址 - 更新于 >>> 2024.03.01 19:57 <<<
    __INUSE_LOGIN_AGAIN_BASE64: str = 'aW51c2UsIGxvZ2luIGFnYWlu'  # inuse, login again 的 Base64 ,重复登录时校园网弹出页面中包含此串。
    __USERID_ERROR1_BASE64: str = 'dXNlcmlkIGVycm9yMQ%3D%3D'  # 账号错误
    __USERID_ERROR2_BASE64: str = 'dXNlcmlkIGVycm9yMg%3D%3D'  # 密码错误
    __AC_AUTHENTICATION_ERROR_CODE: str = 'NTEy'  # AC认证失败

    __wlanacip: str
    __wlanacname: str
    __wlanuserip: str
    __wlanusermac: str

    __wlans_list: list[str]
    __interfaces_list: list[dict]

    def __init__(self):
        self.__wlanacip = ''
        self.__wlanacname = ''
        self.__wlanuserip = ''
        self.__wlanusermac = ''

    def read_wlan_config(self, path='./wlan_config.json') -> bool:
        """
        读取网络配置
        :param path: 网络配置文件路径
        :return:
        """
        try:
            with open(path, 'r') as fp:
                wlan_config = json.load(fp)
                self.__wlanacip = wlan_config['wlanacip']
                self.__wlanacname = wlan_config['wlanacname']
                self.__wlanuserip = wlan_config['wlanuserip']
                self.__wlanusermac = wlan_config['wlanusermac']
        except FileNotFoundError as e:
            return False
        except FileExistsError as e:
            return False
        except json.decoder.JSONDecodeError as e:
            return False
        except IndexError as e:
            return False
        return True

    def save_wlan_config(self, path='./wlan_config.json') -> bool:
        """
        保存网络配置
        :param path: 网络配置文件路径
        :return:
        """
        # 防止空的内容覆盖文件
        if self.__wlanacip + self.__wlanacname + self.__wlanuserip + self.__wlanusermac == '':
            return False
        try:
            wlan_config = {
                'wlanacip': self.__wlanacip,
                'wlanacname': self.__wlanacname,
                'wlanuserip': self.__wlanuserip,
                'wlanusermac': self.__wlanusermac,
            }
            with open(path, 'w') as fp:
                json.dump(wlan_config, fp)
        except FileNotFoundError as e:
            return False
        except FileExistsError as e:
            return False
        return True

    def ccn_update(self, timeout: int = 3) -> bool:
        """
        更新网络信息
        :param timeout: timeout
        :return: 若更新成功，则返回 True ；否则返回 False
        """
        try:
            req_msg: requests.Response = requests.get(self.__WLAN_INFO_REQUEST_URL, allow_redirects=False, timeout=timeout, headers=HEADERS)
            info_url: list[str] = str(req_msg.headers['Location']).split('?')[-1].split("&")
            for expression in info_url:
                var_name, val = expression.split('=')
                if var_name == 'wlanuserip':
                    self.__wlanuserip = val
                if var_name == 'wlanacip':
                    self.__wlanacip = val
                if var_name == 'wlanacname':
                    self.__wlanacname = val
                if var_name == 'wlanusermac':
                    self.__wlanusermac = '-'.join(re.findall(r'\w{1,2}', val[:12]))
        except requests.RequestException as e:
            return self.read_wlan_config()
        # 网络错误，则读取上一次成功后保存的信息
        if req_msg.status_code >= 400:
            return self.read_wlan_config()
        # 请求成功，“抓紧”保存读取到的信息
        self.save_wlan_config()
        return True

    def wlan_update(self) -> bool:
        try:
            self.__wlans_list: list[str] = [wlan['SSID'] for wlan in get_networks_data()]
            self.__interfaces_list: list[dict] = get_interfaces_data()
        except Exception as e:
            return False
        return True

    def act(self, action: ActionBase, timeout: int = 3) -> None | bool:
        """
        执行 ccn.action.Action
        # Example
        ```python
        interactions.act(simple_user.login())
        ```
        :param action: 对校园网的动作，由 User 对象构造的 ActionBase 派生类对象
        :param timeout: timeout
        :return: 若为 None，则为网络问题登录失败；若为 True 则为登录成功；若为 False 则为登录失败。
        """
        # optional todo: 可以优化: if type(...) is ...
        if type(action) is ActionWifi:
            self.wlan_update()
            if action.action == 'wlan_connect':
                if 'SSID' not in self.__interfaces_list[0] or self.__interfaces_list[0]['SSID'] != action.param and action.param in self.__wlans_list:
                    return disconnect() and connect(action.param)
                else:
                    return True
            if action.action == 'wlan_disconnect':
                return disconnect()

        if type(action) is ActionLog:
            url: str = action.url.format(wlanuserip=self.__wlanuserip, wlanacip=self.__wlanacip, wlanacname=self.__wlanacname, wlanusermac=self.__wlanusermac)
            try:
                req_msg = requests.post(url, data=action.param, timeout=timeout, headers=HEADERS)
                # 校园网登录信息的特征反应在了返回页面的标题中
                # 所以这里就通过正则表达式来获取标题内容。
                keywords: str = ''.join(re.findall(r'<title>(.*?)</title>', req_msg.text))
                # 如果是特殊登录状态，他们会在url里加入参数ErrMsg=[错误代码]，通常是Base64编码，也可能会用缩写。
                if self.__INUSE_LOGIN_AGAIN_BASE64 in req_msg.url:
                    # "Inuse, login again" 的重复登录情况
                    return False
                elif '成功' in keywords:
                    # 登录成功
                    return True
                elif self.__USERID_ERROR1_BASE64 in req_msg.url:
                    # 账号错误的情况
                    raise ValueError('账号错误')
                elif self.__USERID_ERROR2_BASE64 in req_msg.url:
                    # 密码错误的情况
                    raise ValueError('密码错误')
                elif self.__AC_AUTHENTICATION_ERROR_CODE in req_msg.url:
                    # AC认证失败
                    # 这个没什么大不了的，直接退出重进就可以了。
                    raise ConnectionRefusedError('“AC认证失败。”账号退出并重进即可。')
                return False
            except requests.RequestException:
                return None
        return None

    @property
    def wlanacip(self) -> str:
        return self.__wlanacip

    @property
    def wlanacname(self) -> str:
        return self.__wlanacname

    @property
    def wlanuserip(self) -> str:
        return self.__wlanuserip

    @property
    def wlanusermac(self) -> str:
        return self.__wlanusermac
