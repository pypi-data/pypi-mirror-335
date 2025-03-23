import copy
import math
import os
from pathlib import Path
from typing import List, Tuple, Union
Seq = Union[List, Tuple]
try:
    from wcwidth import wcswidth
except ImportError:
    print("[text table] 请先安装wcwidth库: pip install wcwidth")

class MyDict:
    def __init__(self, init_dict = None):
        self.dict = dict()
        if init_dict is dict:
            self.dict = init_dict
        if init_dict is MyDict:
            self.dict = init_dict.dict


    def update(self, other_dict):
        self.dict.update(other_dict)

    def items(self):
        return self.dict.items()
    def keys(self):
        return self.dict.keys()
    def values(self):
        return self.dict.values()
    def __getitem__(self, item):
        return self.dict[str(item)]

    def __setitem__(self, key, value):
        key, value = str(key), str(value)

        if key not in self.dict.keys():
            self.dict.update({key: ''})

        self.dict[key] = value

class BAutoTable:
    def __init__(self, x_name='x', y_name='y'):
        self.x_sidebars = []
        self.y_sidebars = []
        self.x_name = x_name
        self.y_name = y_name
        self.dict = dict()
        self._widths = dict()

    def set(self, x_sidebar, y_sidebar, content):
        x_sidebar, y_sidebar, content = str(x_sidebar), str(y_sidebar), str(content)
        self.dict[x_sidebar][y_sidebar] = str(content)

    def get(self, x_sidebar, y_sidebar):
        return self.dict[x_sidebar][y_sidebar]
    def items(self):
        '''
        (key1, key2, value)
        '''
        result = [(x, y, self.dict[x][y]) for x in self.x_sidebars for y in self.y_sidebars]
        return result

    def read_txt(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()
            lines = [x.strip() for x in lines if x.startswith('|')]

        temp = []
        for string in lines:
            elements = string.split('|')[1:-1]
            elements = [x.strip() for x in elements]
            temp.append(elements)

        x_name, y_name = temp[0][0].split(' \\ ')
        x_keys = [var[0] for var in temp[1:]]
        y_keys = temp[0][1:]

        self.x_sidebars = []
        self.y_sidebars = []
        self.x_name = x_name
        self.y_name = y_name
        self.dict = dict()
        self._widths = dict()

        for i, x_element in enumerate(x_keys):
            y_dict = MyDict()
            for j, y_element in enumerate(y_keys):
                y_dict.update({y_element: temp[i+1][j+1]})
            self.dict.update({x_element: y_dict})
    def to_txt(self, path):
        dir = Path(path).resolve().parent
        os.makedirs(dir, exist_ok=True)
        with open(path, 'w') as f:
            f.write(self.get_table_by_str())


    def get_table_by_strs(self) -> List[str]:
        results = self._create_prefix()

        self._update_widths()

        str_dash = ''
        str_head = ''
        for y in self.y_sidebars:
            pre_space, suf_space = self._get_prefix_suffix(y, self._widths[y], ' ')
            pre_dash, suf_dash = self._get_prefix_suffix('-', self._widths[y], '-')
            str_head += ' ' + pre_space + y + suf_space + ' |'
            str_dash += '-' + pre_dash + '-' + suf_dash + '-+'
        results[0] += str_dash
        results[1] += str_head
        results[2] += str_dash

        offset = 3
        for index, y_dicts in enumerate(self.dict.values()):
            for key in self.y_sidebars:
                value = y_dicts[key] if key in y_dicts.keys() else ''
                pre_space, suf_space = self._get_prefix_suffix(value, self._widths[key], ' ')
                str_content = ' ' + pre_space + value + suf_space + ' |'
                results[index+offset] += str_content

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

    def _update_sidebars(self):
        self.x_sidebars = self.dict.keys()

        temp = []
        for dict_y in self.dict.values():
            for key in dict_y.keys():
                if key not in temp:
                    temp.append(key)
        self.y_sidebars = temp

    def _create_prefix(self):
        '''
        得到
        +-------+
        | x \ y |
        +-------+
        |   1   |
        |   2   |
        |   3   |
        +-------+
        '''
        results = []

        title = self.x_name + " \ " + self.y_name
        self._update_sidebars()
        n = self._get_maxlength_from_list(self.x_sidebars)
        length = max(n, self._get_width(title))

        pre_dash, suf_dash = self._get_prefix_suffix("-", length, '-')
        str_dash = "+-" + pre_dash + "-" + suf_dash + "-+"
        results.append(str_dash)

        pre_space, suf_space = self._get_prefix_suffix(title, length, ' ')
        str_index = "| " + pre_space + title + suf_space + " |"
        results.append(str_index)
        results.append(str_dash)

        for x in self.x_sidebars:
            pre_space, suf_space = self._get_prefix_suffix(x, length, ' ')
            str_number = "| " + pre_space + x + suf_space + " |"
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

    def _get_maxlength_from_list(self, lst: List[str]) -> int:
        temp = [self._get_width(x) for x in lst]
        if len(temp) == 0:
            return 0
        else:
            return max(temp)

    def _update_widths(self):
        temp = {key: self._get_width(key) for key in self.y_sidebars}

        for dict_y in self.dict.values():
            for key, value in dict_y.items():
                width = self._get_width(value)
                if width > temp[key]:
                    temp[key] = width

        self._widths = temp


    def _get_width(self, string):
        return wcswidth(string)

    def __len__(self):
        return len(self.x_sidebars) * len(self.y_sidebars)
    def __contains__(self, item):
        for x in self.x_sidebars:
            for y in self.y_sidebars:
                if str(item) == self.dict[x][y]:
                    return True
        return False
    def __str__(self):
        return self.get_table_by_str()

    def __getitem__(self, index):
        index = str(index)

        if index not in self.dict.keys():
            self.dict.update({index: MyDict()})

        return self.dict[str(index)]
    def __setitem__(self, index, value:dict):
        index, value = str(index), MyDict(value)

        if index not in self.dict.keys():
            self.dict.update({index: value})

        self.dict[index] = value

if __name__ == '__main__':
    my_table = BAutoTable("x", "y")

    my_table[1][3] = 123
    my_table[2][2] = 123
    my_table["awa"]["12133"] = 123

    my_table.read_txt(r'E:\byzh_workingplace\byzh-rc-to-pypi\awa.txt')
    print(my_table)
