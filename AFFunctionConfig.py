import os
from pathlib import Path

class CFunctionConfig:

    def config2file(self, path, config):
        # print(path)
        keys = config.value_map.keys()
        keys = list(keys)
        keys.sort()
        if len(keys) > 0:
            start = keys[0][0]
        with open(path, 'w', encoding='utf-8') as f:
            for key in keys:
                if key[0] != start:
                    start = key[0]
                    f.write(f'\n')
                value = config.value_map[key].value
                describe = config.value_map[key].describe
                if describe != '':
                    f.write(f'# {describe}\n')
                f.write(f'{key}={value}\n')


    def file2config(self, path, config):
        # print(path)
        with open(path, 'r', encoding='utf8') as f:

            for line in f.readlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                tempkv = line.split('=', 1)
                if len(tempkv) != 2:
                    raise Exception(f'line {line} error')
                key = tempkv[0].strip()
                # 支持行内註釋：鍵值後面的 # 及其後內容將被忽略
                value = tempkv[1].split('#', 1)[0].strip()

                config.setValue(key, value)

                if key == "D4_FOLDER_PREDICT_SAVE":
                    if not os.path.exists(config.getValue(key)):
                        os.makedirs(config.getValue(key))

                # p_EqualSign = line.find('=')

                # if -1 == p_EqualSign:
                #     pass
                # else:
                #     self.__soldierParseLine(line, config)

class CFunctionGetWebINI:
    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)
        self._load_config()

    def _load_config(self):
        """读取配置文件并解析 IP 和端口"""
        self.config = {}
        try:
            with open(self.path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):  # 忽略空行和注释
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)  # 分割键值对
                        self.config[key.strip()] = value.strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {self.path} 不存在")

    def get_ip(self) -> str:
        """获取 AF_WEB_IP 的值"""
        return self.config.get('AF_WEB_IP', '')

    def get_port(self) -> str:
        """获取 AF_WEB_PORT 的值"""
        return self.config.get('AF_WEB_PORT', '')
    



"""    def __soldierParseLine(self, line, config):

        p_EqualSign = line.find('=')
        key = line[:p_EqualSign]
        value = line[p_EqualSign + 1:]
        value = value.strip()

        try:
            value = float(value)
        except:
            pass
        if key == 'PATH_IMAGE':
            config.D1_PATH_IMAGE = value
        elif key == 'TYPE_IMAGE':
            config.D2_TYPE_IMAGE = value
        elif key == 'TYPE_FLOW':
            config.M1_TYPE_FLOW = value
        elif key == 'DIR_EXPORT':
            config.E1_DIR_EXPORT = value
        elif key == 'PATH_MODEL':
            config.M2_PATH_MODEL = value
        elif key == 'PATH_TRAIN_YAML':
            config.D3_PATH_TRAIN_YAML = value
        elif key == 'PATH_SAVE_IMAGE':
            config.D4_FOLDER_PREDICT_SAVE = value"""