# 长沙理工大学校园网助手

![Language](https://img.shields.io/github/languages/top/jensentsts/csust-campus-net) ![License](https://img.shields.io/github/license/jensentsts/csust-campus-net) 

长沙理工大学校园网助手（CSUST Campus Net Assistant, CCN Assistant）

![CSUST](https://bkimg.cdn.bcebos.com/pic/d8f9d72a6059252df4af0a753b9b033b5bb5b902?x-bce-process=image/resize,m_lfit,w_536,limit_1/quality,Q_70)

本项目基于 [https://github.com/linfangzhi/CSUST_network_auto_login/tree/master](https://github.com/linfangzhi/CSUST_network_auto_login/tree/master) 二次开发，旨在让电脑方便快捷地连接到万年不优化的校园网。

# 特点

## 支持多账号

你可以储存多个账号信息，当某一个账号无法成功连接到校园网时，此工具可以直接连接到其他账号所对应的校园网热点上并尝试连接。

如果某个运营商的校园网炸了，可以直接跳转到你的好朋友的网络上去，~~并把他挤掉……~~

## 状态判断

### 监测账号密码的正误

可以判断账号、密码的正误，如果错误将报错。

### 登录冲突

可以尝试解决`AC认证失败`这样的问题。

### 持续检测是否断网

尝试连接任务完成后，此工具会询问是否要继续运行以持续监测网络连接状况。如果出现无法上网的情况，此工具将会重新开始前面的连接、登录、验证连接状态的步骤。

# 使用说明

## 初次使用

初次使用的用户，可以按照以下步骤完成有关配置。

### 检查校园网状态

- 拥有可以登录校园网的账号；
- 保证你的校园网可以手动登录；

### 写入用户信息

[创建或编辑用户资料](#创建或编辑用户资料)并保存。

### 运行软件

运行`CCN.exe`。

## 必要的文件

```
"CCN目录\"
├─ CCN.exe
├─ users.json
├─ settings.json
└─ address_data.json
```

### 创建或编辑用户资料

您可以参照`users(example).json`中的写法，在main.py同一目录下创建`users.json`，并将您的用户数据填入其中。

| account | password | ccn_ssid  |
|---------|----------|-----------|
| 校园网登录账号 | 校园网登录密码  | 校园网wifi名称 |

*当`users.json`缺失时，该文件不会被自动创建。需要手动创建并依照格式填写有关内容。*

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

设置保存在程序目录下的`settings.json`中。如果配置文件不存在，程序将自动创建一份默认的`settings.json`。

`settings.json`包含多项配置和功能，请参考以下内容：

```json
{
  "log": true,  /* 是否打印日志 */
  "user": {  /* 用户相关配置 */
    "default": 0  /* 默认用户序号 */
  },
  "keep_mode": {  /* 保持工作状态相关配置 */
    "delay": 45  /* 每次循环的延时时长（秒） */
  },
  "net": {  /* 网络相关配置 */
    /*******************************************************************************/
    "timeout": 3,  /* timeout，大致是创建https请求时的重试次数，涉及到网络 */
    "test": {  /* 在检测网络是否可以连接时，向test.url所指的连接发送请求，并判断返回信息中是否包含了test.label */
      "url": "https://www.baidu.com/",  /* 用于检测是否可以上网的连接 */
      "label": "baidu"  /* 检测标签 */
    }
  }
}
```

# 命令行

CCN助手支持通过命令行传入参数。

*（这不是必须的，在编辑好用户数据文件后，您可以直接启动`CCN.exe`）*

## 用户

- `--user`与`-u`等价

通过`--user [索引值]`指定用户信息。这在大多数场合下是必须的

### 什么是索引值

索引值，简单来说，就是每条用户数据对应的编号。

**索引值从0开始**，也就是说，`第一个用户`的索引值为`0`，以此类推。例如，让第一个用户登录，您应该这样写：

```
CCN.exe --user 0 -li
```

### 查询

- `--check`与`-c`等价

配合`--user`，通过`--check`查询指定用户的数据。

```
CCN.exe --user 1 -c
```

## 登录/退出

- `--login`与`-li`等价
- `--logout`与`-lo`等价

例如，让第一个用户登录，您应该这样写：

```
CCN.exe --user 0 -li
```

## 保持循环执行任务

- `--keep`与`-k`等价

附加`--keep`可以让您指定的任务循环执行，每次执行间隔为`settings.json`中的`keep_mode/delay` **秒**

例如：

```
CCN.exe --user 1 -lo --keep
```
`--keep`可以加在任意合适的位置上。

可以让CCN助手循环执行任务，每次任务间隔为`settings.json`中的`keep_mode/delay` **秒**。

## 查询版本号

- `--version`与`-v`、`-V`等价

例如：

```
CCN.exe -v
```

# TODO

- [x] 重构Python代码
- [ ] 使用Rust重构
- [ ] 实现窗口化

# 文档

此项未定。
