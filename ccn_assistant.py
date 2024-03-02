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
        except (FileExistsError, FileNotFoundError) as e:
            with open('./settings.json', 'w') as fp:
                json.dump(SETTINGS_DEFAULT, fp)
                self.__settings = SETTINGS_DEFAULT

    def __log(self, *args):
        if self.__settings['log']:
            self.__console.log(*args)

    def __show_user(self, user:User, index: int | None = None):
        if index is not None:
            self.__log(f'{index}\t{user.data["account"]}: {user.data["ccn_ssid"]}, {user.data["password"]}')
        else:
            self.__log(f'{user.data["account"]}: {user.data["ccn_ssid"]}, {user.data["password"]}')

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

    def add_user(self, user: User) -> bool:
        """
        添加用户
        :param user: 新用户
        :return:
        """
        for u in self.__users_list:
            if u.data == user.data:
                return False
        self.__users_list.append(user)
        return True

    def edit_user(self, user: User) -> bool:
        """
        编辑用户信息
        :param user: 用户
        :return:
        """
        for u in self.__users_list:
            if u.data['account'] == user.data['account']:
                u.data['password'] = user.data['password']
                u.data['ccn_ssid'] = user.data['ccn_ssid']
                return True
        return False

    def remove_user(self, user: User | int) -> bool:
        """
        移除用户
        :param user: 用户
        :return:
        """
        if type(user) is int:
            if user < len(self.__users_list):
                self.__users_list.remove(self.__users_list[user])
                return True
            return False
        for u in self.__users_list:
            if u.data == user.data:
                self.__users_list.remove(u)
        return False

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

    def __wlan_update(self, user: User):
        timeout: int = self.__settings['net']['timeout']
        retry_times: int = self.__settings['net']['retry_times']
        for times in range(retry_times, 0, -1):
            if self.__interactions.act(user.wlan_connect()):
                self.__show_user(user)
                self.__log(user.data['ccn_ssid'])
                break
            time.sleep(3)
        self.__interactions.ccn_update(timeout=timeout)
        self.__log('wlanacip', self.__interactions.wlanacip)
        self.__log('wlanacname', self.__interactions.wlanacname)
        self.__log('wlanuserip', self.__interactions.wlanuserip)
        self.__log('wlanusermac', self.__interactions.wlanusermac)

    def user_logout(self, user: int | User, wlan_connection: bool) -> bool:
        """
        用户退出登录
        :param user: User 对象 或 user索引
        :param wlan_connection: 是否需要wlan连接
        :return:
        """
        timeout: int = self.__settings['net']['timeout']
        if type(user) is int:
            user = self.__users_list[user]
        # wlan
        if wlan_connection:
            self.__wlan_update(user)
        # 不知道为什么，学校的退出登录一向非常管事，即使是尚未登录的账号也能正常跳转到注销登录页面。所以不需要retry_times.
        self.__interactions.act(user.logout(), timeout=timeout)
        return True  # 必定会成功！直接返回 True 就可以了！根本不用担心！（注释于2024.03.01 20:45）

    def user_login(self, user: int | User, wlan_connection: bool) -> bool:
        """
        用户登录
        :param user: User 对象
        :param wlan_connection: 是否需要wlan连接
        :return:
        """
        timeout: int = self.__settings['net']['timeout']
        retry_times: int = self.__settings['net']['retry_times']

        if type(user) is int:
            user = self.__users_list[user]
        # wlan
        if wlan_connection:
            self.__wlan_update(user)
        # ccn log in
        for times in range(retry_times, 0, -1):
            try:
                statue: None | bool = self.__interactions.act(user.login(), timeout=timeout)
                if statue is None:
                    self.user_logout(user, wlan_connection)
                    continue
                if statue:
                    return True
            except BaseException as e:
                self.__log(e)
                return False
            time.sleep(3)
        return False

    def users_login(self) -> bool:
        """
        所有用户尝试登录
        :return: 是否有一个用户登陆成功
        """
        wlan_connection: bool = self.__settings['net']['wlan_connection']

        for index, user in enumerate(self.__users_list):
            try:
                if self.user_login(user, wlan_connection):
                    return True
            except ConnectionRefusedError as e:  # AC认证失败会抛出 ConnectionRefusedError
                self.__log(e)
                self.user_logout(user, wlan_connection)
            except ValueError as e:
                self.__log(e)
                self.__show_user(user=user, index=index)
                return False
            finally:
                time.sleep(3)
        return False

    def keep_inspecting(self):
        """
        保持对网络的检测
        """
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
                self.__log('[green]Success')
                time.sleep(delay)
            else:
                self.__log('[red]Failed')
                time.sleep(3)

    def list_users(self, user: User | int | None = None):
        self.__log('[bright_white]Users List')
        if user is None:
            for index, user in enumerate(self.__users_list):
                self.__show_user(user=user, index=index)
        else:
            if type(user) is User:
                self.__show_user(user=user, index=None)
            if type(user) is int:
                self.__show_user(user=self.__users_list[user], index=user)

    @property
    def user(self) -> list[User]:
        return self.__users_list

    @property
    def settings(self) -> dict:
        return self.__settings

    @property
    def interactions(self) -> Interactions:
        return self.__interactions
