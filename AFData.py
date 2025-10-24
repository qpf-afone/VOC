import numpy as np

from enum import Enum, unique

@unique
class EnumFlow(Enum):

    Predict = 0
    Train1 = 1
    Train2 = 2
    Val = 3

class CINI: 
    AF_WEB_IP = '127.0.0.1'
    AF_WEB_PORT = 5000

class ConfigLine:
    value = ''
    diff = ''
    describe = ''
    def __init__(self, value, describe, ):
        self.value = value
        self.diff = value
        self.describe = describe
    
    
class Config:

    value_map = {
        'D1_PATH_IMAGE': ConfigLine('', '图片路径'),
        'D2_TYPE_IMAGE': ConfigLine('jpg', '图片类型'),
        'D3_PATH_TRAIN_YAML': ConfigLine('', '训练yaml路径'),
        'M1_TYPE_FLOW': ConfigLine(EnumFlow.Predict.value, '流程类型'),

        'E1_DIR_EXPORT': ConfigLine('', '导出路径'),
        'M2_PATH_MODEL': ConfigLine('', '模型路径'),
        'D4_FOLDER_PREDICT_SAVE': ConfigLine('', '模型预测结果输出路径'),
        'M3_TYPE_MODEL': ConfigLine(0, '模型类型'),

        'P1_PREDICT_CONFIDENCE': ConfigLine(0.3, '模型预测置信度'),

        'V1_VAL_PATH': ConfigLine('', '模型验证路径')
    }

    def getValue(self, key):
        if key not in self.value_map:
            raise KeyError(f'key {key} not in config')
        return self.value_map[key].value

    def setValue(self, key, value):
        if key not in self.value_map:
            raise KeyError(f'key {key} not in config')
        try:
            self.value_map[key].value = int(value)
        except:
            self.value_map[key].value = value
        try:
            self.value_map[key].value = float(value)
        except:
            self.value_map[key].value = value
        # self.value_map[key].value = value

class CDataPack:
    myCFG = Config()

    myIMAGE = np.empty([1, 1])
    # poetry
    