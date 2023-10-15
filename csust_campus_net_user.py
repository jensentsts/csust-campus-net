import json


users_file_path = './campus_users_data.json'


# 用户类
#
# 为什么 users_file_path 中保存了多个用户的数据：
# - 在长理校园网抽风的时候，你可能需要借用一下同学的校园网
# - 方便我做不同运营商网络连接的测试
class User:
    campus_net_ssid: str
    username: str
    account: str
    password: str

    def __init__(self):
        self.username = 'Unnamed'  # 用户名，此处指的不是登录校园网用的账户名，仅仅是显示在软件内部的名称，不作登录用
        self.campus_net_ssid = 'csust-yd'  # 校园网网络名称
        self.account = '000000000000'  # 校园网登录账号
        self.password = '000000'  # 校园网登录密码

    # 设置账户数据
    #
    # 账户数据包含了以下信息：
    # - 校园网网络名称 campus_net_name
    # - 校园网登录账号 account
    # - 校园网登录密码 password
    def set_account_data(self, campus_net_name, account, password):
        self.campus_net_ssid = campus_net_name
        self.account = account
        self.password = password

    # 设置数据
    def set_data(self, data: dict):
        self.username = data['username']
        self.campus_net_ssid = data['campus_net_ssid']
        self.account = data['account']
        self.password = data['password']

    # 转化为json
    def get_package(self) -> dict:
        return dict(username=self.username, campus_net_ssid=self.campus_net_ssid, account=self.account,
                    password=self.password)


# 读取用户数据
def load_users_data(path: str) -> list[User]:
    data = ''
    try:
        with open(path, mode='r+', encoding='utf-8') as file:
            while True:
                line = file.readline()
                if not line:
                    break
                data += line
    except [FileNotFoundError, FileExistsError]:
        with open(path, mode='w+', encoding='utf-8') as file:
            file.write('[]')
        data = '[]'
    data_dict = json.loads(data)
    users_list = []
    for i in data_dict:
        user = User()
        user.set_data(i)
        users_list += [user]
    return users_list


# 保存用户数据
def save_users_data(path: str, users_data: list[User]):
    users_packages = []
    for i in users_data:
        users_packages += [i.get_package()]
    users_json = json.dumps(users_packages)
    with open(path, mode='w', encoding='utf-8') as file:
        file.write(users_json)
