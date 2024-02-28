# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:58
# @Author  : jensentsts
# @File    : ccn_interactions.py.py
# @Description : 与长理校园网进行交互
import re

from .action import Action
import requests


class Interactions:
    __WLAN_INFO_REQUEST_URL: str = 'http://1.1.1.1/?isReback=1'  # get 以用于获取网络信息
    __INUSE_LOGIN_AGAIN_BASE64: str = 'aW51c2UsIGxvZ2luIGFnYWlu'  # inuse, login again 的 Base64

    __wlanacip: str
    __wlanacname: str
    __wlanuserip: str
    __wlanusermac: str

    def __init__(self):
        self.__wlanacip = ''
        self.__wlanacname = ''
        self.__wlanuserip = ''
        self.__wlanusermac = ''
        self.update()

    def update(self, timeout: int = 3) -> bool:
        """
        更新网络信息
        :param timeout: timeout
        :return: 若更新成功，则返回 True ；否则返回 False
        """
        try:
            req_msg: requests.Response = requests.get(self.__WLAN_INFO_REQUEST_URL, allow_redirects=False, timeout=timeout)
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
            return False
        return True

    def act(self, action: Action, timeout: int = 3) -> None | bool:
        """
        执行 CCN_Action
        # Example
        ```python
        interactions.act(simple_user.login())
        ```
        :param action: 对校园网的动作，由 User 对象构造的 CCN_Action 对象
        :param timeout: timeout
        :return: 若为 None，则为网络问题登录失败；若为 True 则为登录成功；若为 False 则为登录失败。
        """
        url: str = action.url.format(wlanuserip=self.__wlanuserip, wlanacip=self.__wlanacip, wlanacname=self.__wlanacname, wlanusermac=self.__wlanusermac)
        try:
            req_msg = requests.post(url, data=action.param, timeout=timeout)
            # 校园网登录信息的特征反应在了返回页面的标题中
            # 所以这里就通过正则表达式来获取标题内容。
            keywords: str = ''.join(re.findall(r'<title>(.*?)</title>', req_msg.text))
            if self.__INUSE_LOGIN_AGAIN_BASE64 in keywords:
                # "Inuse, login again" 的重复登录情况
                return False
            elif '成功' in keywords:
                # 登录成功
                return True
            return False
        except requests.RequestException:
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
