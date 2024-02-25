# 长沙理工大学校园网自动登录器
![Language](https://img.shields.io/github/languages/top/jensentsts/csust-campus-net) ![License](https://img.shields.io/github/license/jensentsts/csust-campus-net) 

<div align="center"><img src="https://bkimg.cdn.bcebos.com/pic/d8f9d72a6059252df4af0a753b9b033b5bb5b902?x-bce-process=image/resize,m_lfit,w_536,limit_1/quality,Q_70"></div>

本项目基于[https://github.com/linfangzhi/CSUST_network_auto_login/tree/master](https://github.com/linfangzhi/CSUST_network_auto_login/tree/master)二次开发，联网成功后会再次提示本项目的开源信息。感谢学长的项目，学弟在研究过程中省了不少麻烦。

此工具旨在让电脑方便快捷地连接到万年不优化登录过程的学校校园网。

长沙理工大学校园网(CSUST campus net)下缩写为CCN。

## 初次使用
首先要保证你拥有校园网。

接着，你需要保证软件同目录下有用户数据文件`ccn_user_data.xlsx`，你可以参考[用户数据文件](#用户数据文件)中的说明编辑它。

确保wifi处于打开状态，启动后，软件会读取用户数据，并连接到相应的校园网热点上。

### 建立用户数据文件
默认的用户数据文件路径是软件所在目录下的`ccn_user_data.xlsx`。

你可以自行创建用户数据文件，也可以在首次启动软件`ccn_auto_login`后，打开软件自动创建的用户数据文件。请在文件里写入用户数据并保存，例如：

| 用户名 | 账号 | 密码 | ssid |
| :---: | :---: | :---: | :---:|
| test | 202xyyyyzzzz | 123456 | csust-yd |

*ssid：就是wifi名，例如csust-yd、csust-dx、csust-lt、csust-bg等*

写入用户数据后，才可以连接到网络。

用户数据文件的路径在`csust_campus_net_user.py`中，你可以在这里更改它。

## 特点

### 支持多账号
你可以储存多个账号信息，当某一个账号无法成功连接到校园网时，此工具可以直接连接到其他账号所对应的校园网热点上并尝试连接。

如果某个运营商的校园网炸了，可以直接跳转到你的好朋友的网络上去，~~并把他挤掉……~~

### 自动连接wifi
使用`subprocess`，根据账号数据文件里的ssid信息，连接到对应的校园网热点上。

### 自动解决登录冲突
如果此前在其他设备上登录了校园网，或在同一设备上登录校园网，长理校园网会在“信息页”上写明"inuse, login again"的字样。但是可惜我们不能通过“信息页”来判断是否是重复登录界面，因为其他错误（例如账号密码错误等）为避免跨域请求或项目可维护性降低等问题（猜测）也使用了这个页面。

此工具将会 在登录期间调用的post方法的返回信息中 查找 请求url里 是否有"inuse, login again"的base64编码（aW51c2UsIGxvZ2luIGFnYWlu） 来判断是否为重复登录，接着向校园网请求注销，然后重新登录此账号。

### 自动检测是否断网
尝试连接任务完成后，此工具会询问是否要继续运行以持续监测网络连接状况。如果出现无法上网的情况，此工具将会重新开始前面的连接、登录、验证连接状态的步骤。

## 其它
- 三大运营商的校园网（csust-yd、csust-dx、csust-lt）的自动登录均已通过测试
- 自测稳定，不确定其他状况下是否能正常运行。

## todos
- 账号密码正误消息提示。
- 使用体验优化
- 优化说明文件
- 自动注册windows服务并隐藏到后台
- release一个打包后的文件
