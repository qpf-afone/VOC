import numpy as np
import cv2
from AFFunctionModel import CFunctionModel
from abc import abstractmethod

import os

from AFSystem import SOFTWARE_NAME

class CTaskBase:
    def __init__(self, inputDP):
        self.dp = inputDP
        self.cfg = inputDP.myCFG
    @abstractmethod
    def work(self):
        pass
    
class CTaskCheck(CTaskBase):
    # 有很多东西可以check：内、外存、文件等等；
    def work(self):
        # todo
        #  检查文件是否存在
        #  检查文件是否被打开
        #  检查内存、显卡
        #  检查网络
        #  如果不合格，报错崩
        # 目前只做最小检查：关键路径是否存在
        predict_save_folder = self.cfg.getValue('D4_FOLDER_PREDICT_SAVE')
        if predict_save_folder:
            os.makedirs(predict_save_folder, exist_ok=True)
        return True


class CTaskReadImage(CTaskBase):

    def work(self):
        # todo
        # 调用function对图片进行处理
        # 读取图片
        # 标准化
        self.dp.myIMAGE = cv2.imread(self.cfg.getValue('D1_PATH_IMAGE'))
        

class CTaskPredict(CTaskBase):

    def work(self):
        # 只做推理，不保存
        fm = CFunctionModel()
        result = fm.predict_no_save(
            model_path=self.cfg.getValue('M2_PATH_MODEL'),
            source=self.cfg.getValue('D1_PATH_IMAGE'),
            conf=float(self.cfg.getValue('P1_PREDICT_CONFIDENCE')),
        )
        self.dp.predict_result = result

class CTaskExport(CTaskBase):

    def work(self):
        # 仅负责导出（保存可视化/标签），必要时再次调用保存模式
        fm = CFunctionModel()
        save_dir = self.cfg.getValue('D4_FOLDER_PREDICT_SAVE') or None
        if not save_dir:
            return
        os.makedirs(save_dir, exist_ok=True)
        result = fm.save_visualization(
            model_path=self.cfg.getValue('M2_PATH_MODEL'),
            source=self.cfg.getValue('D1_PATH_IMAGE'),
            save_dir=save_dir,
            conf=float(self.cfg.getValue('P1_PREDICT_CONFIDENCE')),
        )
        self.dp.predict_result = result

class CTaskTrain(CTaskBase):

    def work(self):
        fm = CFunctionModel()
        result = fm.train(
            data_yaml_path=self.cfg.getValue('D3_PATH_TRAIN_YAML'),
            pretrained_model_path=self.cfg.getValue('M2_PATH_MODEL'),
            project_dir=self.cfg.getValue('E1_DIR_EXPORT') or None,
            run_name='train',
        )
        self.dp.train_result = result

class CTaskVal(CTaskBase):
    def work(self):
        fm = CFunctionModel()
        result = fm.validate(
            model_path=self.cfg.getValue('M2_PATH_MODEL'),
            data_yaml_path=self.cfg.getValue('D3_PATH_TRAIN_YAML'),
        )
        self.dp.val_result = result
