from ...writer import BWriter
from ...tools.text_style import BColor
from ...tools.text_table import BRowTable
from typing import Union
import time

Iter = Union[list, set, tuple]

def grid_trains_1d(func, iters: Iter, log_path):
    """
    x从iters中取
    :param func: 只有一个输入参数x, 返回值将转化为str并记录
    :param iters:
    :param log_path:
    :return:
    """
    print(f"{BColor.CYAN}=====================")
    print("grid_trains_1d 将在3秒后开始:")
    print(f"====================={BColor.RESET}")
    time.sleep(3)

    my_writer = BWriter(log_path, ifTime=False)
    my_writer.toFile("[grid_trains] 开始", ifTime=True)
    my_table = BRowTable(["x", "result"])

    for x in iters:
        result = func(x)
        my_table.add([x, result])

    strs = my_table.get_table_by_strs()
    for x in strs:
        my_writer.toFile(x)
    my_writer.toFile("[grid_trains] 结束", ifTime=True)

def grid_trains_2d(func, iters1: Iter, iters2: Iter, log_path):
    print(f"{BColor.CYAN}=====================")
    print("grid_trains_2d 将在3秒后开始:")
    print(f"====================={BColor.RESET}")
    time.sleep(3)

    my_writer = BWriter(log_path, ifTime=False)
    my_writer.toFile("[grid_trains] 开始", ifTime=True)
    my_table = BRowTable(["x", "y", "result"])
    for x in iters1:
        for y in iters2:
            result = func(x, y)
            my_table.add([x, y, result])

    strs = my_table.get_table_by_strs()
    for x in strs:
        my_writer.toFile(x)
    my_writer.toFile("[grid_trains] 结束", ifTime=True)

if __name__ == '__main__':
    def function(x):
        return x

    grid_trains_1d(function, [1,2,3], './awa.txt')
