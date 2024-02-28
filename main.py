# -*- coding: utf-8 -*-
# @Time    : 2024/2/28 20:35
# @Author  : jensentsts
# @File    : main.py
# @Description :

import ccn_assistant


if __name__ == '__main__':
    assistant = ccn_assistant.CCN_Assistant()
    assistant.load('./users.json')
    assistant.keep_inspect()
