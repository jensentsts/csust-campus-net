# coding=utf-8
from rich.progress import TextColumn, BarColumn, TimeRemainingColumn, TimeElapsedColumn

from ccn_instructions import *
from ccn_auto_login import *
import time
from rich import progress


# 启动!
if __name__ == '__main__':
    instructions()
    while True:
        # 自动登录
        for try_times in range(settings['net']['reconnect_try_times'], 0, -1):
            if login():
                rule('连接成功')
                break
            else:
                info(f'登录失败，尝试重新登录. 剩余重试次数 {try_times} .')
                time.sleep(2)
        with progress.Progress(TextColumn("[progress.description]{task.description}"),
                               BarColumn(),
                               TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                               TimeRemainingColumn(),
                               TimeElapsedColumn()) as prog:
            waiting = prog.add_task('[yellow]距下次检测', total=settings['net']['test']['delay'])
            for i in range(int(settings['net']['test']['delay'])):
                time.sleep(1)
                prog.update(waiting, advance=1)
