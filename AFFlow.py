from AFLogging import INFO_TO_USER_FLOW1, logToUser, INFO_TO_USER_FLOW2, INFO_TO_USER_FLOW3
from AFTask import CTaskCheck, CTaskReadImage, CTaskPredict, CTaskTrain, CTaskVal, CTaskExport
from abc import abstractmethod
class FlowBase:
    def __init__(self, p):
        self.packExp = p

    @abstractmethod
    def run(self):
        pass
    
class Flow1(FlowBase):
    def run(self):
        # check
        logToUser(INFO_TO_USER_FLOW1[0])
        taskCheck = CTaskCheck(self.packExp)
        taskCheck.work()

        # read image
        logToUser(INFO_TO_USER_FLOW1[1])
        taskRead = CTaskReadImage(self.packExp)
        taskRead.work()

        # predict
        logToUser(INFO_TO_USER_FLOW1[2])
        taskPredict = CTaskPredict(self.packExp)
        taskPredict.work()

        # export
        logToUser(INFO_TO_USER_FLOW1[3])
        taskExport = CTaskExport(self.packExp)
        taskExport.work()

class Flow2(FlowBase):
    def run(self):

        # check
        logToUser(INFO_TO_USER_FLOW2[0])
        taskCheck = CTaskCheck(self.packExp)
        taskCheck.work()

        logToUser(INFO_TO_USER_FLOW2[1])
        taskTrain = CTaskTrain(self.packExp)
        taskTrain.work()

class Flow3(FlowBase):
    def run(self):
        logToUser(INFO_TO_USER_FLOW3[0])
        taskCheck = CTaskCheck(self.packExp)
        taskCheck.work()

        logToUser(INFO_TO_USER_FLOW3[1])
        taskVal = CTaskVal(self.packExp)
        taskVal.work()
