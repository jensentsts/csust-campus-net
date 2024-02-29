# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 21:44
# @Author  : jensentsts
# @File    : ccn_assistant.py
# @Description :
import time
from io import TextIOWrapper

import requests

from ccn import User, Interactions
from rich.console import Console
import json
from wifi_actions import get_networks_data, get_interfaces_data, connect, disconnect

SETTINGS_DEFAULT = {
  "log": True,
  "net": {
    "wlan_connection": True,
    "keep_inspect_delay": 60,
    "timeout": 3,
    "retry_times": 3,
    "test": {
      "url": "https://www.baidu.com/",
      "label": "baidu"
    }
  }
}

class CCN_Assistant:
    __users_list: list[User]
    __interactions: Interactions
    __settings: dict
    __console: Console

    def __init__(self):
        """长理校园网帮手"""
        self.__users_list = []
        self.__interactions = Interactions()
        self.__settings = {}
        self.__console = Console()
        try:
            with open('./settings.json', 'r') as fp:
                self.__settings = json.load(fp)
        except FileExistsError | FileNotFoundError as e:
            with open('./settings.json', 'w') as fp:
                json.dump(SETTINGS_DEFAULT, fp)

    def __log(self, *args):
        if self.__settings['log']:
            self.__console.log(*args)

    def load(self, users_data_fp: str | TextIOWrapper | list[dict]):
        """
        加载用户数据和设置
        :param users_data_fp: 用户数据保存对象，可以是存储路径或 TextIOWrapper 对象
        :return:
        """
        users_list: list[dict] = []
        # load
        if type(users_data_fp) is str:
            with open(users_data_fp, 'r') as fp:
                users_list = json.load(fp)
        if type(users_data_fp) is TextIOWrapper:
            users_list = json.load(users_data_fp)
        if type(users_data_fp) is list:
            users_list = users_data_fp
        # parse
        self.__users_list = []
        for user in users_list:
            self.__users_list.append(User(user))

    def add_user(self, user: User):
        self.__users_list.append(user)

    def save(self, users_data_fp: str | TextIOWrapper):
        """
        保存用户数据和设置
        :param users_data_fp: 用户数据保存对象，可以是存储路径或 TextIOWrapper 对象
        :return:
        """
        users_list: list[dict] = []
        # 用户数据保存
        for user in self.__users_list:
            users_list.append(user.data)
        if type(users_data_fp) is str:
            with open(users_data_fp, 'w') as fp:
                json.dump(users_list, fp)
        if type(users_data_fp) is TextIOWrapper:
            json.dump(users_list, users_data_fp)
        # settings.json 保存
        with open('./settings.json', 'w') as fp:
            json.dump(self.__settings, fp)

    def user_logout(self, index: int):
        """
        # 测试中
        用户退出登录
        :param index: 索引
        :return:
        """
        self.__interactions.act(self.__users_list[index].logout())

    def users_login(self) -> bool:
        """
        所有用户尝试登录
        :return: 是否有一个用户登陆成功
        """
        timeout: int = self.__settings['net']['timeout']
        retry_times: int = self.__settings['net']['retry_times']
        wlan_connection: bool = self.__settings['net']['wlan_connection']

        wlan_list: list[str] = []
        if wlan_connection:
            wlan_list = [wlan['SSID'] for wlan in get_networks_data()]
        interfaces = get_interfaces_data()

        for user in self.__users_list:
            for times in range(retry_times, 0, -1):
                self.__interactions.update(timeout=timeout)
                self.__log('wlanacip', self.__interactions.wlanacip)
                self.__log('wlanacname', self.__interactions.wlanacname)
                self.__log('wlanuserip', self.__interactions.wlanuserip)
                self.__log('wlanusermac', self.__interactions.wlanusermac)
                # wlan
                if wlan_connection:
                    if 'SSID' not in interfaces[0] or interfaces[0]['SSID'] != user.ssid and user.ssid in wlan_list:
                        self.__log('connecting...')
                        disconnect()
                        connect(user.ssid)
                        continue
                # CCN
                res: bool | None = self.__interactions.act(user.login(), timeout)
                if res is None:
                    # 尝试退出，在下一次循环中重试
                    self.__interactions.act(user.logout(), timeout)
                    continue
                if res:
                    # 若成功登录，直接结束登录尝试并返回 True
                    return True
        return False

    def keep_inspect(self):
        """保持对网络的检测"""
        test_url: str = self.__settings['net']['test']['url']
        test_label: str = self.__settings['net']['test']['label']
        timeout: int = self.__settings['net']['timeout']
        delay: int = self.__settings['net']['keep_inspect_delay']

        def is_network_ok():
            """网络连接是否正常"""
            try:
                return test_label in requests.get(test_url, timeout=timeout).text
            except requests.RequestException:
                return False

        while True:
            if is_network_ok() or self.users_login():
                self.__log('Success')
                time.sleep(delay)
            else:
                self.__log('Failed')
                time.sleep(3)

    @property
    def user(self) -> list[User]:
        return self.__users_list

    @property
    def settings(self) -> dict:
        return self.__settings

    @property
    def interactions(self) -> Interactions:
        return self.__interactions
