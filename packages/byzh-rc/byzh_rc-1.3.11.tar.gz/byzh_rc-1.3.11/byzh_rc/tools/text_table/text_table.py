import copy
import math
from wcwidth import wcswidth
from typing import List

class BRowTable:
    def __init__(self, head: List):
        self.head = self._lst2str(head)
        self.rows = []
        self.widths = []
        self._update_widths(self.head)

    def add(self, lst: List):
        assert len(lst) == len(self.head), "添加的 行元素个数 与 head元素个数 不一致"
        lst = self._lst2str(lst)
        self._update_widths(lst)
        self.rows.append(lst)

    def get_table_by_strs(self) -> List[str]:
        results = self._create_prefix()

        str_dash = ''
        str_head = ''
        for i, x in enumerate(self.head):
            pre_space, suf_space = self._get_prefix_suffix(x, self.widths[i], ' ')
            pre_dash, suf_dash = self._get_prefix_suffix('-', self.widths[i], '-')
            str_head += ' ' + pre_space + x + suf_space + ' |'
            str_dash += '-' + pre_dash + '-' + suf_dash + '-+'
        results[0] += str_dash
        results[1] += str_head
        results[2] += str_dash

        offset = 3
        for i, row in enumerate(self.rows):
            for j, x in enumerate(row):
                pre_space, suf_space = self._get_prefix_suffix(x, self.widths[j], ' ')
                str_content = ' ' + pre_space + x + suf_space + ' |'
                results[i+offset] += str_content

        results[-1] += str_dash

        return results

    def get_table_by_str(self) -> str:
        result = ""
        strs = self.get_table_by_strs()
        for x in strs[:-1]:
            result += x + '\n'
        result += strs[-1]

        return result

    def print_table(self):
        print(self.get_table_by_str())

    def _create_prefix(self):
        '''
        得到
        +-----+
        | num |
        +-----+
        |  1  |
        |  2  |
        |  3  |
        +-----+
        '''
        results = []
        # 编号的位数
        n = self._get_width(str(len(self.rows)))
        length = max(n, self._get_width("num"))

        pre_dash, suf_dash = self._get_prefix_suffix("-", length, '-')
        str_dash = "+-" + pre_dash + "-" + suf_dash + "-+"
        results.append(str_dash)

        pre_space, suf_space = self._get_prefix_suffix("num", length, ' ')
        str_num = "| " + pre_space + "num" + suf_space + " |"
        results.append(str_num)
        results.append(str_dash)

        for i in range(len(self.rows)):
            number = str(i+1)
            pre_space, suf_space = self._get_prefix_suffix(number, length, ' ')
            str_number = "| " + pre_space + number + suf_space + " |"
            results.append(str_number)
        results.append(str_dash)

        return results



    def _get_prefix_suffix(self, string, length, charactor=' '):
        prefix = ''
        suffix = ''
        str_len = self._get_width(string)

        delta = length - str_len
        if delta < 0:
            assert "string的宽度比length宽"
        elif delta == 0:
            pass
        else:
            prefix = charactor * math.floor(delta / 2)
            suffix = charactor * math.ceil(delta / 2)

        return prefix, suffix

    def _update_widths(self, lst):
        temps = []
        for x in lst:
            temps.append(self._get_width(x))

        if len(self.widths) == 0:
            self.widths = temps
        else:
            for i, x in enumerate(temps):
                if x > self.widths[i]:
                    self.widths[i] = x

    def _lst2str(self, lst):
        lst = copy.deepcopy(lst)
        for i, x in enumerate(lst):
            lst[i] = str(x)

        return lst

    def _get_width(self, string):
        return wcswidth(string)

if __name__ == '__main__':
    my_table = BRowTable(['云编号', '名称', 'IP地址'])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.add(["server01", "服务器01", "172.16.0.1"])
    my_table.print_table()