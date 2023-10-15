from csust_campus_net_user import *
from colorama import Fore, Back, init
from csust_campus_net_instructions import instructions


user_list = []


def create_user_data():
    global user_list
    print(Fore.LIGHTWHITE_EX + '---------------------------------')
    user = User()
    user.username = input('用户名(非登录用): ')
    user.account = input('上网账号(登录用): ')
    user.password = input('密码: ')
    user.campus_net_ssid = 'csust-' + input('校园网ssid: csust-')
    user_list += [user]


def edit_user_data(user: User, user_index: int):
    user_current_index = user_index
    while True:
        print(Fore.LIGHTWHITE_EX + '---------------------------------')
        print('-3. 设置优先级 (当前: ', Fore.LIGHTYELLOW_EX + f'{user_current_index})')
        print('-2. 删除')
        print('-1. 返回菜单')
        print('0. 用户名(非登录用): ', Fore.LIGHTYELLOW_EX + f'{user.username}')
        print('1. 上网账号(登录用): ', Fore.LIGHTYELLOW_EX + f'{user.account}')
        print('2. 密码: ', Fore.LIGHTYELLOW_EX + f'{user.password}')
        print('3. 校园网ssid: ', Fore.LIGHTYELLOW_EX + f'{user.campus_net_ssid}')

        try:
            opt = int(input(Fore.LIGHTWHITE_EX + '操作: '))
        except ValueError:
            print(Fore.LIGHTRED_EX + 'ERR:',
                  Fore.RESET + '非整型!')
            continue

        if opt == -3:
            try:
                set_index = int(input('输入优先级: '))
            except ValueError:
                print(Fore.LIGHTRED_EX + 'ERR:',
                      Fore.RESET + '非整型!')
                continue
            if set_index >= len(user_list):
                user_list.remove(user)
                user_list.append(user)
                user_current_index = len(user_list) - 1
            elif set_index < 0:
                user_list.remove(user)
                user_list.insert(__index=0, __object=user)
                user_current_index = 0
            else:
                user_list.remove(user)
                user_list.insert(set_index, user)
                user_current_index = set_index
        if opt == -2:
            if input('确定删除? (y/n)').lower() == 'y':
                user_list.remove(user)
                break
        if opt == -1:
            break
        if opt == 0:
            user.username = input('输入用户名(非登录用): ')
        if opt == 1:
            user.username = input('输入上网账号(登录用): ')
        if opt == 2:
            user.username = input('输入密码: ')
        if opt == 3:
            user.campus_net_ssid = 'csust-' + input('校园网ssid: csust-')


if __name__ == '__main__':
    init(autoreset=True)
    user_list = load_users_data(users_file_path)
    while True:
        print(Fore.LIGHTWHITE_EX + '=================================')
        print('-4. 保存并退出')
        print('-3. 重新加载')
        print('-2. 新建用户资料')
        print('-1. 保存')
        if len(user_list) == 0:
            print('暂无用户资料')
        else:
            for index, i in enumerate(user_list):
                print(f'{index}. {i.username}')

        try:
            choice = int(input(Fore.LIGHTWHITE_EX + '操作: '))
        except ValueError:
            print(Fore.LIGHTRED_EX + 'ERR:',
                  Fore.RESET + '非整型!')
            continue

        if choice == -4:
            save_users_data(path=users_file_path, users_data=user_list)
            print(Fore.LIGHTWHITE_EX + 'INFO:', Fore.RESET + f'已保存到路径 {users_file_path}')
            instructions()
            input('按回车键退出')
            exit(0)
        if choice == -3:
            user_list = load_users_data(users_file_path)
            print(Fore.LIGHTWHITE_EX + 'INFO:', Fore.RESET + f'已重新加载文件 {users_file_path}')
        if choice == -2:
            create_user_data()
        if choice == -1:
            save_users_data(path=users_file_path, users_data=user_list)
            print(Fore.LIGHTWHITE_EX + 'INFO:', Fore.RESET + f'已保存到路径 {users_file_path}')

        if choice >= len(user_list):
            print(Fore.LIGHTRED_EX + 'ERR:',
                  Fore.RESET + '数值越界!')
        if len(user_list) > choice >= 0:
            edit_user_data(user_list[choice], choice)
