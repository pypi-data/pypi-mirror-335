from ...writer import BWriter
from typing import Union
import torch

Iter = Union[list, set, tuple]

def get_device(sout=False):
    lst = []
    # 优先使用NPU
    try:
        import torch_npu
        lst.append(torch.device("npu"))
    except ImportError:
        pass

    # 其次使用GPU
    if torch.cuda.is_available():
        lst.append(torch.device("cuda"))

    # 最后使用CPU
    lst.append(torch.device("cpu"))

    lst_str = [str(i) for i in lst]
    if sout:
        print(f"可用设备:{lst_str}, 使用{lst_str[0]}")
    return lst[0]


def grid_trains_1d(func, iters: Iter, log_path):
    """
    x从iters中取
    :param func: 只有一个输入参数x, 返回值将转化为str并记录
    :param iters:
    :param log_path:
    :return:
    """
    my_writer = BWriter(log_path)
    for x in iters:
        result = func(x)
        my_writer.toFile(str(x) + " -> " + str(result))

def grid_trains_2d(func, iters1: Iter, iters2: Iter, log_path):
    my_writer = BWriter(log_path)
    for x in iters1:
        for y in iters2:
            result = func(x, y)
            my_writer.toFile(str(x) + "|" + str(y) + " -> " + str(result))


if __name__ == '__main__':
    result = get_device()
    print(result)