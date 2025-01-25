# -*- coding: utf-8 -*-
# @Time    : 2025/1/24 下午5:33
# @Author  : jensentsts
# @File    : assistant.py
# @Description : 长沙理工大学校园网（登录）助手

import json
import typing

import requests

from ccn import *
import json

CCN_VERSION = "0.3.0"

# 默认设置
SETTINGS_DEFAULT = {
    "title": "校园网助手",
    "user": {
        "default": 0
    },
    "net": {
        "timeout": 3,
        "test": {
            "url": "https://www.baidu.com/",
            "label": "baidu"
        }
    },
    "keep_mode": {
        "delay": 45
    }
}


class Core:
    """ 处理核心 """

    class Path:
        address_data_path: str = './address_data.json'
        settings_path: str = './settings.json'
        users_path: str = './users.json'

    def __settings_dump(self):
        self.ccn.timeout = self.__settings['net']['timeout']

    def __save(self):
        # 用户数据
        with open(self.Path.users_path, 'w', encoding='utf-8') as fp:
            users_list: list[dict] = []
            for u in self.__users:
                users_list.append(u.get_dict())
            json.dump(users_list, fp)
        # 设置数据
        with open(self.Path.settings_path, 'w', encoding='utf-8') as fp:
            json.dump(self.__settings, fp)
        # 地址数据
        with open(self.Path.address_data_path, 'w', encoding='utf-8') as fp:
            json.dump(self.ccn.get_address_data().get_dict(), fp)

    def __load(self):
        """ 载入 """
        # 用户
        with open(self.Path.users_path, 'r', encoding='utf-8') as fp:
            users = json.load(fp)
            self.__users = []
            for u in users:
                self.__users.append(User().set_data(u))
        # 设置及其初始化
        try:
            with open(self.Path.settings_path, 'r', encoding='utf-8') as fp:
                self.__settings = json.load(fp)
        except (FileExistsError, FileNotFoundError) as e:
            with open(self.Path.settings_path, 'w', encoding='utf-8') as fp:
                json.dump(SETTINGS_DEFAULT, fp)
                self.__settings = SETTINGS_DEFAULT
        finally:
            self.__settings_dump()
        # address data
        for i in range(0, self.ccn.timeout):
            try:
                # 获取并存储
                self.ccn.update_address_data()
                with open(self.Path.address_data_path, 'w') as fp:
                    json.dump(self.ccn.get_address_data().get_dict(), fp)
                break
            except (AddressDataGetError, AddressDataTimeoutError) as e_net:
                # 如果已经获取了 self.ccn.timeout 次而未获得结果，则尝试读取原来存储的文件。
                if i == self.ccn.timeout - 1:
                    try:
                        with open(self.Path.address_data_path, 'r') as fp:
                            address_data = json.load(fp)
                            self.ccn.set_address_data(AddressData(wlanacip=address_data['wlanacip'],
                                                                  wlanacname=address_data['wlanacname'],
                                                                  wlanuserip=address_data['wlanuserip'],
                                                                  wlanusermac=address_data['wlanusermac']))
                        break
                    except (FileExistsError, FileNotFoundError) as e_file:
                        raise e_net
                else:
                    continue

        self.__save()

    def __init__(self):
        self.__ccn: CCN = CCN()
        self.__users: list[User] = []
        self.__settings: dict = {}

        self.__load()

    @property
    def ccn(self) -> CCN:
        return self.__ccn

    @property
    def timeout(self) -> int:
        return self.ccn.timeout

    @timeout.setter
    def timeout(self, value: int):
        self.ccn.timeout = value

    @property
    def settings(self) -> dict:
        return self.__settings

    def get_users(self) -> list[User]:
        """ 获取用户 """
        return self.__users

    def add_user(self, u: User) -> typing.Self:
        """ 添加用户 """
        self.__users.append(u)
        return self

    def remove_user(self, u: [User | int]) -> typing.Self:
        """ 删除用户 """
        if type(u) is User:
            self.__users.remove(u)
        else:
            self.__users.remove(self.__users[u])
        return self

    def get_timeout(self) -> int:
        return self.ccn.timeout

    def set_timeout(self, timeout) -> typing.Self:
        self.ccn.__timeout = timeout
        return self

    def login(self, user_index: int) -> typing.Self:
        """ 用户登录 """
        for counter in range(0, self.ccn.timeout):
            try:
                if self.ccn.statue:
                    break
                self.ccn.login(self.__users[user_index])
            except (AcAuthenticationError, InuseLoginAgainError):
                self.ccn.logout(self.__users[user_index]).login(self.__users[user_index])
                continue
        return self

    def logout(self, user_index: int) -> typing.Self:
        """ 用户退出 """
        self.ccn.logout(self.__users[user_index])
        return self

    def net_statue_test(self) -> bool:
        """ 网络状态测试 """
        try:
            label = self.__settings['net']['test']['label']
            url = self.__settings['net']['test']['url']
            return label in requests.get(url, timeout=self.timeout).text
        except (requests.RequestException, requests.Timeout):
            return False
