from AFFlow import Flow1, Flow2, Flow3
from AFData import CDataPack
from AFFunctionConfig import CFunctionGetWebINI
from AFSystem import INFO_TO_USER_Staff, SOFTWARE_NAME, IO_INI_WEB_CONFIG
from AFLogging import logToUser
from flask import Flask
from AFRoute import CMyRoute
import os   

# ---------- 全局初始化（只执行一次） ----------
# 若需要禁用 GPU，可开启下一行
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# ---------- Flask 应用 ----------
app = Flask(__name__)


# 这个就是把web服务启动起来
class AFStaff_server:
    def __init__(self):
        pass

    def start(self, inputArgv: list[str]):
        logToUser(f"inputArgv: {inputArgv}")
        # 读INI文件，得到IP和端口
        myWebINI = CFunctionGetWebINI(IO_INI_WEB_CONFIG)
        logToUser(f"IP: {myWebINI.get_ip()}, Port: {myWebINI.get_port()}")

        # 注册路由
        self._register_routes()

        # 把FLASK启动
        app.run(myWebINI.get_ip(), int(myWebINI.get_port()), threaded=False)
        pass

    def _register_routes(self):
        """注册所有路由"""
        route_handler = CMyRoute()
        route_handler.register_routes(app)
