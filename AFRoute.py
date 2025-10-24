from flask import request, jsonify, Response
import tempfile
from pathlib import Path
from AFSystem import SOFTWARE_NAME
from AFStaff import AFStaff 
from AFWeb_UI import register_ui_routes

class CMyRoute:
    def __init__(self):
        self.TEMP_DIR = Path(tempfile.gettempdir(), "afserver_cfgs")
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    def register_routes(self, app):
        """注册所有路由到 Flask 应用"""

        @app.route("/staff/process", methods=["POST"])
        def staff_process():
            """
            POST 接口：处理配置文件
            接收 multipart/form-data：
              - 字段名必须为 config
              - 内容为配置文件
            """
            if "config" not in request.files:
                return jsonify({"error": "请使用字段名 config 上传配置文件"}), 400

            f = request.files["config"]
            cfg_path = self.TEMP_DIR / f.filename
            f.save(cfg_path)

            try:
                # 调用 Staff 业务    # 跑单机版的Staff
                staff = AFStaff()
                result = staff.start(["", cfg_path])
                return jsonify({"status": "ok", "result": result}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @app.route("/staff/status", methods=["GET"])
        def staff_status():
            """
            GET 接口：获取系统状态
            """
            return jsonify({
                "software_name": SOFTWARE_NAME,
                "version": "202X.XX",
                "status": "running",
                "endpoints": {
                    "process": "POST /staff/process - 处理配置文件",
                    "status": "GET /staff/status - 系统状态"
                }
            }), 200

        # 将 UI 路由从独立模块注册进来
        register_ui_routes(app, self.TEMP_DIR)


