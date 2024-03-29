# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:35
# @Author  : jensentsts
# @File    : ccn_user.py
# @Description : 长理校园网用户类

from .action import ActionLog, ActionWifi


class User:
    __account: str  # 账号
    __password: str  # 密码
    __ccn_ssid: str  # 校园网 SSID

    def __init__(self, data: dict | None = None):
        if data is None:
            self.__account = ''
            self.__password = ''
            self.__ccn_ssid = ''
        else:
            self.__account = data['account']
            self.__password = data['password']
            self.__ccn_ssid = data['ccn_ssid']

    @property
    def ssid(self) -> str:
        return self.__ccn_ssid

    @property
    def data(self) -> dict:
        return {
            'account': self.__account,
            'password': self.__password,
            'ccn_ssid': self.__ccn_ssid,
        }

    @data.setter
    def data(self, value: dict[str, str]):
        self.__account = value['account']
        self.__password = value['password']
        self.__ccn_ssid = value['ccn_ssid']

    def login(self) -> ActionLog:
        return ActionLog('login', self.__account, self.__password)

    def logout(self) -> ActionLog:
        return ActionLog('logout', self.__account, self.__password)

    def wlan_connect(self) -> ActionWifi:
        return ActionWifi('wlan_connect', self.__ccn_ssid)

    def wlan_disconnect(self) -> ActionWifi:
        return ActionWifi('wlan_disconnect', self.__ccn_ssid)

