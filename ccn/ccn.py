# -*- coding: utf-8 -*-
# @Time    : 2025/1/24 下午4:21
# @Author  : jensentsts
# @File    : ccn.py
# @Description : 长沙理工大学校园网（CSUST Campus Net）
import re
import typing
from enum import Enum

import requests

from .user import User


class AddressData:
    """ 地址数据 """

    def __init__(self,
                 wlanuserip: str | None = None,
                 wlanacip: str | None = None,
                 wlanacname: str | None = None,
                 wlanusermac: str | None = None):
        self.wlanuserip: str | None = wlanuserip
        self.wlanacip: str | None = wlanacip
        self.wlanacname: str | None = wlanacname
        self.wlanusermac: str | None = wlanusermac

    def __bool__(self):
        return ((type(self.wlanuserip) is str and
                type(self.wlanacip) is str and
                type(self.wlanacname) is str and
                type(self.wlanusermac) is str) or
                (self.wlanuserip is None and
                 self.wlanacip is None and
                 self.wlanacname is None and
                 self.wlanusermac is None))

    def __repr__(self):
        return (f"wlanuserip={self.wlanuserip}\n"
                f"wlanacip={self.wlanacip}\n"
                f"wlanacname={self.wlanacname}\n"
                f"wlanusermac={self.wlanusermac}\n")

    def get_dict(self) -> dict[str, str | None]:
        """ 转换为dict类型 """
        return {
            'wlanuserip': self.wlanuserip,
            'wlanacip': self.wlanacip,
            'wlanacname': self.wlanacname,
            'wlanusermac': self.wlanusermac,
        }

    def clear(self) -> typing.Self:
        self.wlanuserip = None
        self.wlanacip = None
        self.wlanacname = None
        self.wlanusermac = None
        return self


class AcAuthenticationError(ConnectionError):
    """ Ac 认证失败 """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class InuseLoginAgainError(ConnectionError):
    """ Inuse, login again. """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class AccountError(ValueError):
    """ 账号错误 """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class PasswordError(ValueError):
    """ 密码错误 """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class AddressDataGetError(ConnectionError):
    """ 密码错误 """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class AddressDataTimeoutError(ConnectionError):
    """ 地址数据获取超时错误 """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class UnrecordedError(ConnectionError):
    """ 未被记录的错误 """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class CCN:
    """"""

    class RequestData:
        """
        请求相关的数据
        """

        # address_data_request_url: str = 'http://1.1.1.1/?isReback=1'  # get 以用于获取网络信息 较旧的网址 仍然可用 - 注释于 ->> 2024.03.01 19:57 <<-
        url_address_data_request: str = 'http://gstatic.com/'  # get 以用于获取网络信息 较新的网址 - 更新于 >>> 2024.03.01 19:57 <<<
        url_login: str = 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Login&protocol=http:&hostname=192.168.7.221&iTermType=1&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&mac={wlanusermac}&ip={wlanuserip}&enAdvert=0&queryACIP=0&loginMethod=1'
        url_logout: str = 'http://192.168.7.221:801/eportal/?c=ACSetting&a=Logout&wlanuserip={wlanuserip}&wlanacip={wlanacip}&wlanacname={wlanacname}&port=&hostname=192.168.7.221&iTermType=1&session=&queryACIP=0&mac={wlanusermac}'
        request_headers: dict = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "",
        }  # Headers

    class Codes:
        """ 返回结果的代码 """

        success: str = '成功'  # 成功登录，UTF-8
        inuse_login_again: str = 'aW51c2UsIGxvZ2luIGFnYWlu'  # inuse, login again 的 Base64 ,重复登录时校园网弹出页面中包含此 Base64 字符串。
        userid_error1: str = 'dXNlcmlkIGVycm9yMQ%3D%3D'  # 账号错误
        userid_error2: str = 'dXNlcmlkIGVycm9yMg%3D%3D'  # 密码错误
        ac_authentication_error: str = 'NTEy'  # AC认证失败

    def __post(self,
               url,
               param):
        """ post请求并对结果做一些预处理 """
        req = requests.post(url=url, data=param, headers=self.RequestData.request_headers, timeout=self.__timeout)
        # 校园网登录信息的特征反应在了返回页面的标题中
        # 所以这里就通过正则表达式来获取标题内容。
        keywords: str = ''.join(re.findall(r'<title>(.*?)</title>', req.text))

        cases = {
            lambda: self.Codes.success in keywords: True,
            lambda: self.Codes.inuse_login_again in req.url: (False, InuseLoginAgainError('inuse, login again')),
            lambda: self.Codes.userid_error1 in req.url: (False, AccountError('账号错误')),
            lambda: self.Codes.userid_error2 in req.url: (False, PasswordError('密码错误')),
            lambda: self.Codes.ac_authentication_error in req.url: (False, AcAuthenticationError('AC认证失败')),
        }
        for func in cases:
            if func():
                return cases[func]
        return False, UnrecordedError(f'未知错误\n{keywords}\n{req.url}\n')

    def __init__(self,
                 address_data: AddressData = AddressData(),
                 timeout: int = 3):
        self.__address_data: AddressData = address_data
        self.__statue: bool = False
        self.__timeout: int = timeout
        self.set_address_data(address_data)

    @property
    def statue(self) -> bool:
        """ 登录状态 """
        return self.__statue

    @property
    def timeout(self) -> int:
        return self.__timeout

    @timeout.setter
    def timeout(self, value: int):
        self.__timeout = value

    def get_address_data(self) -> AddressData:
        return self.__address_data

    def set_address_data(self,
                         address_data: AddressData) -> typing.Self:
        """
        设置地址数据
        :param address_data: 设备地址数据
        :return:
        """
        if not address_data:
            raise ValueError(f"地址数据错误！{address_data}")
        self.__address_data = address_data
        return self

    def update_address_data(self) -> typing.Self:
        """更新设备的地址数据"""
        self.__address_data.clear()
        try:
            req_msg: requests.Response = requests.get(self.RequestData.url_address_data_request,
                                                      allow_redirects=False,
                                                      timeout=self.__timeout,
                                                      headers=self.RequestData.request_headers)
            info_url: list[str] = str(req_msg.headers['Location']).split('?')[-1].split("&")
            for expression in info_url:
                var_name, val = expression.split('=')
                if var_name == 'wlanuserip':
                    self.__address_data.wlanuserip = val
                if var_name == 'wlanacip':
                    self.__address_data.wlanacip = val
                if var_name == 'wlanacname':
                    self.__address_data.wlanacname = val
                if var_name == 'wlanusermac':
                    # self.__address_data.wlanusermac = '-'.join(re.findall(r'\w{1,2}', val[:12]))
                    self.__address_data.wlanusermac = '-'.join(val[i:i+2] for i in range(0, 11, 2))
        except (requests.RequestException, ValueError, KeyError) as e:
            raise AddressDataGetError('地址数据获取异常')
        # 网络错误
        if req_msg.status_code >= 400:
            raise AddressDataTimeoutError('地址数据获取网络错误')
        return self

    def login(self,
              user: User,
              raise_exception: bool = True) -> typing.Self:
        self.__statue, ex = self.__post(url=self.RequestData.url_login.format(wlanuserip=self.__address_data.wlanuserip,
                                                                              wlanacip=self.__address_data.wlanacip,
                                                                              wlanacname=self.__address_data.wlanacname,
                                                                              wlanusermac=self.__address_data.wlanusermac),
                                        param=user.get_param())
        if raise_exception and ex is not None:
            raise ex
        return self

    def logout(self,
               user: User,
               raise_exception: bool = True) -> typing.Self:
        self.__statue, ex = self.__post(url=self.RequestData.url_logout.format(wlanuserip=self.__address_data.wlanuserip,
                                                                               wlanacip=self.__address_data.wlanacip,
                                                                               wlanacname=self.__address_data.wlanacname,
                                                                               wlanusermac=self.__address_data.wlanusermac),
                                        param=user.get_param())
        if raise_exception and ex is not None:
            raise ex
        return self
