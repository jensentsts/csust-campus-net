import pandas as pd

user_data_path = r'.\csust_campus_net_user_data.xlsx'


# 用户类
#
# 为什么 users_file_path 中保存了多个用户的数据：
# - 在长理校园网抽风的时候，你可能需要借用一下同学的校园网
# - 方便我做不同运营商网络连接的测试
# - TODO: 制作可视化窗口
class User:
    username: str
    account: str
    password: str
    campus_net_ssid: str

    def __init__(self):
        self.username = 'Unnamed'  # 用户名，此处指的不是登录校园网用的账户名，仅仅是显示在软件内部的名称，不作登录用
        self.account = '000000000000'  # 校园网登录账号
        self.password = '000000'  # 校园网登录密码
        self.campus_net_ssid = 'csust-xx'  # 校园网网络名称

    def set_data(self, data: dict):
        self.username = data['username']
        self.account = data['account']
        self.password = data['password']
        self.campus_net_ssid = data['campus_net_ssid']

# 读取用户数据
def load_users_data(path: str) -> list[User]:
    data = []
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        empty_data = {'用户名': [], '账号': [], '密码': [], 'ssid': []}
        df = pd.DataFrame(empty_data)
        df.to_excel(path)
    else:
        sheet = pd.read_excel(path, sheet_name=0)
        username = sheet['用户名']
        account = sheet['账号']
        password = sheet['密码']
        campus_net_ssid = sheet['ssid']
        for i in range(0, len(username)):
            data += [dict(username=username[i], account=account[i], password=password[i],
                          campus_net_ssid=campus_net_ssid[i])]

    users_list = []
    for i in data:
        user = User()
        user.set_data(i)
        users_list += [user]
    return users_list
