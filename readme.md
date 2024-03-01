# 长沙理工大学校园网自动登录器
![Language](https://img.shields.io/github/languages/top/jensentsts/csust-campus-net) ![License](https://img.shields.io/github/license/jensentsts/csust-campus-net) 

![CSUST](https://bkimg.cdn.bcebos.com/pic/d8f9d72a6059252df4af0a753b9b033b5bb5b902?x-bce-process=image/resize,m_lfit,w_536,limit_1/quality,Q_70)

本项目基于[https://github.com/linfangzhi/CSUST_network_auto_login/tree/master](https://github.com/linfangzhi/CSUST_network_auto_login/tree/master)二次开发，联网成功后会再次提示本项目的开源信息。感谢学长的项目，学弟在研究过程中省了不少麻烦。

此工具旨在让电脑方便快捷地连接到万年不优化登录过程的学校校园网。

长沙理工大学校园网(CSUST campus net)下缩写为CCN。

*作者非计通专业。欢迎校友们多多提供Issues、PR和添加Stars！*

# 特点

## 支持多账号

你可以储存多个账号信息，当某一个账号无法成功连接到校园网时，此工具可以直接连接到其他账号所对应的校园网热点上并尝试连接。

如果某个运营商的校园网炸了，可以直接跳转到你的好朋友的网络上去，~~并把他挤掉……~~

## 自动连接wifi

使用`subprocess`，根据账号数据文件里的ssid信息，断开非目标网络的连接，并连接到对应的校园网热点上。

## 状态判断

### 监测账号密码的正误

可以判断账号、密码的正误，如果错误将报错。

### 登录冲突

可以尝试解决`AC认证失败`这样的问题。

### 持续检测是否断网

尝试连接任务完成后，此工具会询问是否要继续运行以持续监测网络连接状况。如果出现无法上网的情况，此工具将会重新开始前面的连接、登录、验证连接状态的步骤。

# 初次使用

首先要保证你拥有校园网。

确保wifi功能处于打开状态，启动后，软件会读取用户数据，并连接到相应的校园网热点上。

在文件下载完成后，您必须要先[创建您的用户资料文件](#编辑用户资料文件)。

此外，您也可以[配置设置](#配置设置)。常用的配置已经在settings.json中写好，您可以直接使用本软件而不需编辑。

关于更多的可能，您可以查看[使用说明](#使用说明)

# 使用说明

## 文件

```
"CCN目录\"
├─ users.json
├─ settings.json
└─ wlan_config.json
```

### 编辑用户资料文件

您可以参照`users(example).json`中的写法，在main.py同一目录下创建`users.json`，并将您的用户数据填入其中。

| account | password | ccn_ssid  |
|---------|----------|-----------|
| 校园网登录账号 | 校园网登录密码  | 校园网wifi名称 |

*该文件不会被自动创建。*

例如，你可以这样写：

```json
[
  {
    "account": "202105050505",
    "password": "111111",
    "ccn_ssid": "csust-yd"
  }
]
```

当然了，示例中的账号信息显然是不合法的。

### 配置设置

设置保存在程序目录下的`settings.json`中。如配置文件不存在，程序将自动创建一个新的settings.json。

在settings.json中，你可以配置许多功能。请看示例：

```json
{
  "log": true,  /*是否打印日志*/
  "net": {  /*网络相关配置*/
    "wlan_connection": true,  /*自动连接到wifi*/
    "keep_inspect_delay": 60,  /*保持网络检测的检测间隔*/
    /*******************************************************************************/
    "timeout": 3,  /*timeout，大致是创建https请求时的重试次数，涉及到网络*/
    "retry_times": 3,  /*重试次数，这是在登录到某一个账号时，尝试登录此账号的次数，与网络无直接关系*/
    "test": {  /*在检测网络是否可以连接时，向test.url所指的连接发送请求，并判断返回信息中是否包含了test.label*/
      "url": "https://www.baidu.com/",  /*用于检测是否可以上网的连接*/
      "label": "baidu"  /*标签*/
    }
  }
}
```
## 指令参数

如果你通过命令行调用CCN，那么您将可以更加灵活地使用您的账号。

*此条目*

## 其它

- 三大运营商的校园网（csust-yd、csust-dx、csust-lt）的自动登录均已通过测试
- 自测稳定，不确定其他状况下是否能正常运行。

## 

## 二次开发

~~这……应该不会有吧~~看看有没有人可能需要我为这个库写点什么再说吧。
