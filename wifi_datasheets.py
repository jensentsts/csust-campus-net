# -*- coding: utf-8 -*-
# @Time    : 2024/2/12 19:03
# @Author  : jensentsts
# @File    : wifi_actions.py
# @Description :

import re
import subprocess


def get_interfaces_data() -> list[dict]:
    wifi_list = []
    cmd_output = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], check=True, text=True, capture_output=True).stdout

    data = re.sub(r'系统上有 \d+ 个接口:\n', '', cmd_output)
    pattern = re.compile(r'\s*([^:\n]+)\s*:\s*([^:\n]+(?:\s*:\s*[^:\n]+)*)\s*\n')
    matches = pattern.findall(data)

    new_wifi = {}
    for key, value in matches:
        if '个接口' in key:
            continue
        # 奇怪的是，key后面总是会跟着很长的空格，但是上面的正则单独拿出来测试就没问题。
        new_wifi[re.sub(r'\s+$', '', key)] = re.sub(r'\s+$', '', value)
        if '络状' in key:  # 网络状态
            wifi_list.append(new_wifi)
            new_wifi = {}
    return wifi_list


def get_networks_data() -> list[dict]:
    network_list = []
    cmd_output = subprocess.run(['netsh', 'wlan', 'show', 'networks'], check=True, text=True, capture_output=True).stdout

    data = re.sub(r"当前有 \d+ 个网络可见。", '', cmd_output)
    data = re.sub(r"SSID \d+", "SSID", data)
    pattern = re.compile(r'\s*([^:\n]+)\s*:\s*([^:\n]+(?:\s*:\s*[^:\n]+)*)\s*\n')
    matches = pattern.findall(data)

    new_network = {}
    for key, value in matches:
        if '当前有' in key:
            continue
        if '口名' in key:  # 接口名称
            continue
        new_network[re.sub(r'\s+$', '', key)] = re.sub(r'\s+$', '', value)
        if '加密' in key:
            network_list.append(new_network)
            new_network = {}
    return network_list
