# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:47
# @Author  : jensentsts
# @File    : ccn_action.py
# @Description : 对校园网的动作
import typing


class ActionBase:
    _action: str
    _param: typing.Any

    def __init__(self, action: str, param: typing.Any):
        """
        操作基类
        :param action: 操作名
        """
        self._action = action
        self._param = param

    @property
    def action(self) -> str:
        return self._action

    @property
    def param(self) -> typing.Any:
        return self._param


class ActionWifi(ActionBase):
    __ssid: str

    def __init__(self, action: str, ssid: str):
        """
        Wifi操作
        :param action: 操作名
        :param ssid: wlan ssid
        """
        super().__init__(action, ssid)


class ActionLog(ActionBase):
    __URL = {
        'login': 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Login&protocol=http:&hostname=192.168.7.221&iTermType=1&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&mac={wlanusermac}&ip={wlanuserip}&enAdvert=0&queryACIP=0&loginMethod=1',
        'logout': 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Logout&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&port=&hostname=192.168.7.221&iTermType=1&session=&queryACIP=0&mac={wlanusermac}',
    }

    def __param_constructor(self, account: str, password: str) -> dict:
        """
        参数构造器
        :param account:
        :param password:
        :return:
        """
        return {
            'DDDDD': ',0,{0}'.format(account),
            'upass': '{0}'.format(password),
            'R1': '0',
            'R2': '0',
            'R3': '0',
            'R6': '0',
            'para': '00',
            '0MKKey': '123456',
        }

    def __init__(self, action: str, account: str, password: str):
        """
        校园网登录/退出操作
        :param action: 操作名（"login"/"logout"）
        :param account: 账号
        :param password: 密码
        """
        super().__init__(action, self.__param_constructor(account, password))

    @property
    def url(self) -> str:
        return self.__URL[self._action]
