# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:35
# @Author  : jensentsts
# @File    : ccn_user.py
# @Description : 长理校园网用户类
import typing


class User:
    __account: str  # 账号
    __password: str  # 密码
    __ccn_ssid: str  # 校园网 SSID

    def __init__(self,
                 data: dict[str, str] | None = None):
        if data is None:
            self.__account = ''
            self.__password = ''
            self.__ccn_ssid = ''
        else:
            self.__account = data['account']
            self.__password = data['password']
            self.__ccn_ssid = data['ccn_ssid']

    def __repr__(self) -> str:
        return f'account: {self.__account}\n'

    def get_account(self) -> str:
        return self.__account

    def set_account(self,
                    account: str) -> typing.Self:
        self.__account = account
        return self

    def get_password(self) -> str:
        return self.__password

    def set_password(self,
                     psw: str) -> typing.Self:
        self.__password = psw
        return self

    def get_ssid(self) -> str:
        return self.__ccn_ssid

    def set_ssid(self,
                 ccn_ssid: str) -> typing.Self:
        self.__ccn_ssid = ccn_ssid
        return self

    def get_dict(self) -> dict:
        return {
            'account': self.__account,
            'password': self.__password,
            'ccn_ssid': self.__ccn_ssid,
        }

    def set_data(self,
                 value: dict[str, str]) -> typing.Self:
        self.__account = value['account']
        self.__password = value['password']
        self.__ccn_ssid = value['ccn_ssid']
        return self

    def get_param(self) -> dict:
        return {
            'DDDDD': ',0,{0}'.format(self.__account),
            'upass': '{0}'.format(self.__password),
            'R1': '0',
            'R2': '0',
            'R3': '0',
            'R6': '0',
            'para': '00',
            '0MKKey': '123456',
        }

