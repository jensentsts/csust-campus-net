# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:47
# @Author  : jensentsts
# @File    : ccn_action.py
# @Description : 对校园网的动作

class Action:
    __param: dict
    __action: str

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
        校园网操作
        :param action: 操作名（"login"/"logout"）
        :param account: 账号
        :param password: 密码
        """
        self.__action = action
        self.__param = self.__param_constructor(account, password)

    @property
    def param(self) -> dict:
        return self.__param

    @property
    def url(self) -> str:
        return self.__URL[self.__action]
