# -*- coding: utf-8 -*-

import datetime
from AFData import CDataPack, EnumFlow, CINI
from AFFunctionConfig import CFunctionConfig
from AFFlow import Flow1, Flow2, Flow3
from AFSystem import INFO_TO_USER_Staff, SOFTWARE_NAME
import time
from AFLogging import logToUser

class AFStaff:

    def start(self, argv):
        """原有 CLI 命令行方式，保留兼容性"""
        start_time = time.time()
        logToUser(INFO_TO_USER_Staff[0])
        self.__checkTime()

        n = len(argv)
        packExp = CDataPack()
        fc = CFunctionConfig()

        if n == 1:
            fc.config2file('config.txt', packExp.myCFG)
        elif n == 2:
            fc.file2config(argv[1], packExp.myCFG)
            self.__runFlow(packExp)
        else:
            info = 'Run AFStaff with this command: python AFStaff parameter_file'
            logToUser(info)

        end_time = time.time()
        logToUser(f"\n[{SOFTWARE_NAME}] Task finish in %.4lfs.\n" % (end_time - start_time))


    def __runFlow(self, packExp):
        """提取公共流程调用逻辑"""
        mtf = packExp.myCFG.getValue('M1_TYPE_FLOW')
        if mtf == EnumFlow.Predict.value:
            Flow1(packExp).run()
        elif mtf == EnumFlow.Train1.value:
            Flow2(packExp).run()
        elif mtf == EnumFlow.Val.value:
            Flow3(packExp).run()
        else:
            logToUser("Unknown flow type.")



    @staticmethod
    def __checkTime():
        pass
        # dateNow = datetime.datetime.now()
        # dateDead = datetime.datetime(EXPIRATION_TIME['Year'], EXPIRATION_TIME['Month'], EXPIRATION_TIME['Day'], 23, 59)

        # n_day = (dateDead - dateNow).days

        # #print("MSStaff63: "+str(n_day))

        # if n_day < 0:

        #     logGetError(INFO_TO_USER_Staff[0])

        # elif n_day < 7:

        #     logToUser(INFO_TO_USER_Staff[1])

        # else:

        #     logToUser(INFO_TO_USER_Staff[2])
        #     logToUser(str(dateNow))
