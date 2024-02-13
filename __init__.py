# coding=utf-8
from csust_campus_net_auto_login import *
import

# 启动!
if __name__ == '__main__':
    keep_inspecting = False  # 是否要持续监测网络连接状态

    init(autoreset=True)

    instructions()
    while True:
        # 自动登录
        for try_times in range(settings['net']['timeout'], 0, -1):
            if login():
                break
            else:
                info(f'登录失败，尝试重新登录. 剩余重试次数 {try_times} .')
        # 持续检测网络状态
        if '{0}y{1}'.format(keep_inspecting, input(
                '{0} {1}INFO:{2} 是否持续检测网络连接状态? (y or any): '.format(time.strftime('[%H:%M:%S]',
                                                                                             time.localtime()),
                                                                               Fore.LIGHTWHITE_EX,
                                                                               Fore.RESET)).lower()):
            keep_inspecting = True
            info(f'每隔 {settings["net"]["test"]["delay"]} 秒检测一次网络状况.')

            while True:
                # 延时
                if settings['log']['show_net_test_delay_bar']:
                    time_delay_bar = tqdm(range(settings['net']['test']['delay']),
                                          desc='{0} {1}INFO:{2} 距下一次网络检测'.format(
                                              time.strftime('[%H:%M:%S]', time.localtime()), Fore.LIGHTWHITE_EX,
                                              Fore.RESET),
                                          unit='meow', leave=False, file=sys.stdout)
                    for i in time_delay_bar:
                        time.sleep(1)
                else:
                    time.sleep(settings['net']['test']['delay'])
                # 检测
                if not is_network_ok(success_info=settings['log']['show_net_test_succession_info']):
                    failed('网络连接异常!')

                    break
        else:
            break
    # input('按回车退出. ')
    exit(0)
