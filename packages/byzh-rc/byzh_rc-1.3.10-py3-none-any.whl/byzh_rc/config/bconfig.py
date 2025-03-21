from ..drawer.terminal import BColor
from ..basic import Byzh
class BConfig(Byzh):
    def __init__(self):
        super().__init__()
        self.dict = dict()

    # set-方法
    def set(self, key, value):
        if not isinstance(key, str):
            raise Exception(f"{BColor.YELLOW}key({str(key)}) must be str{BColor.RESET}")

        self.dict[key] = value

    # show-方法
    def show_all(self):
        print(self)

    # get-方法
    def get_str(self, key):
        self.__check(key)
        return str(self.dict[key])
    def get_int(self, key):
        self.__check(key)
        return int(self.dict[key])
    def get_float(self, key):
        self.__check(key)
        return float(self.dict[key])
    def get_bool(self, key):
        '''
        只有value为["False", "0", "None"]时，返回False
        '''
        self.__check(key)

        if self.get_str(key) in ["False", "0", "None"]:
            return False
        elif self.get_str(key) in ["True", "1"]:
            return True
        else:
            raise Exception(f"{BColor.YELLOW}value({str(key)}) cannot change to bool{BColor.RESET}")

    # save-方法
    def to_pickle(self, path):
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.dict, f)
    def from_pickle(self, path):
        import pickle
        with open(path, 'rb') as f:
            self.dict = pickle.load(f)
    def to_json(self, path):
        import json
        with open(path, 'w') as f:
            json.dump(self.dict, f)

    def from_json(self, path):
        import json
        with open(path, 'r') as f:
            self.dict = json.load(f)

    def to_yaml(self, path):
        import yaml
        with open(path, 'w') as f:
            yaml.dump(self.dict, f)
    def from_yaml(self, path):
        import yaml
        with open(path, 'r') as f:
            self.dict = yaml.load(f, Loader=yaml.FullLoader)
    def to_ini(self, path):
        import configparser
        config = configparser.ConfigParser()
        config['config'] = self.dict
        with open(path, 'w') as f:
            config.write(f)

    def from_ini(self, path):
        import configparser
        config = configparser.ConfigParser()
        config.read(path)
        self.dict = dict(config['config'])

    def to_csv(self, path):
        import csv
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            for key, value in self.dict.items():
                writer.writerow([key, value])

    def from_csv(self, path):
        import csv
        with open(path, 'r') as f:
            reader = csv.reader(f)
            self.dict = {rows[0]: rows[1] for rows in reader}

    # 工具-方法
    def __str__(self):
        result = "default:\n" + "\n".join([f"\t({key} -> {value})" for key, value in self.dict.items()])
        return result
    def __check(self, key):
        # 检查key是否是字符串
        if not isinstance(key, str):
            raise Exception(f"{BColor.YELLOW}key({str(key)}) must be str{BColor.RESET}")



if __name__ == '__main__':
    a = BConfig()

    a.set('a', 'None')
    a.set('b', '123')
    a.set('345', '33333')
    a.set('a532', 'No32ne')
    a.set('b13', '123412')
    a.set('321345', '33342333')

    a.to_csv('config.csv')
    a.from_csv('config.csv')
    a.to_yaml('config.yaml')
    a.from_yaml('config.yaml')
    a.to_pickle('config.pkl')
    a.from_pickle('config.pkl')
    a.to_json('config.json')
    a.from_json('config.json')

    print(a.get_str('b13'))
    print(a)