from flask import request, jsonify, Response, redirect
from pathlib import Path
from AFSystem import SOFTWARE_NAME
from AFStaff import AFStaff
from AFFunctionModel import CFunctionModel
import base64


def register_ui_routes(app, temp_dir: Path) -> None:
    # 根路径重定向到 /ui
    @app.route("/", methods=["GET"])
    def _root_redirect():
        return redirect("/ui", code=302)

    """注册简易 Web UI 的两个路由：/ui 与 /ui/predict。
    参数
    - app: Flask 实例
    - temp_dir: 用于暂存上传图片与临时配置的目录
    """

    @app.route("/ui", methods=["GET"])
    def ui_index():
        html = f"""
<!doctype html>
<html lang=zh>
<head>
  <meta charset=utf-8 />
  <title>{SOFTWARE_NAME} - 简易控制台</title>
  <style>
    :root {{ --bg:#0b1220; --card:#121a2b; --text:#e6e8ef; --muted:#97a0b0; --accent:#4f7cff; --border:#23304a; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial; margin: 0; background: var(--bg); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 32px auto; padding: 0 20px; }}
    .card {{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border: 1px solid var(--border); border-radius: 14px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }}
    h2 {{ margin: 0 0 16px; font-weight: 700; letter-spacing: .3px; }}
    fieldset {{ border: 1px dashed var(--border); border-radius: 12px; padding: 16px; margin: 18px 0; }}
    legend {{ padding: 0 8px; color: var(--muted); }}
    label {{ display: block; margin: 10px 0 6px; color: var(--muted); }}
    input[type=text], input[type=number] {{ width: 100%; padding: 10px 12px; background: #0e1626; color: var(--text); border: 1px solid var(--border); border-radius: 10px; outline: none; }}
    input[type=text]:focus, input[type=number]:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(79,124,255,0.2); }}
    .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .btn {{ display: inline-block; background: var(--accent); border: none; color: #fff; padding: 10px 18px; border-radius: 10px; cursor: pointer; font-weight: 600; letter-spacing: .2px; }}
    .btn:hover {{ filter: brightness(1.05); }}
    .note {{ color: var(--muted); font-size: 12px; }}
    .ok {{ color: #52ff8f; }}
  </style>
  </head>
  <body>
    <div class="container">
      <div class="card">
        <h2>{SOFTWARE_NAME} - 预测控制台</h2>
        <p class=note>功能：1) 导入现有配置；2) 在线填写参数并选择图片进行预测。</p>

        <fieldset>
          <legend>1. 导入配置文件（等同 POST /staff/process）</legend>
          <form action="/staff/process" method="post" enctype="multipart/form-data">
            <label>选择配置文件（字段名为 config）</label>
            <input type="file" name="config" required />
            <div style="margin-top:10px"><button class="btn" type="submit">上传并运行</button></div>
          </form>
        </fieldset>

        <fieldset>
          <legend>2. 在线填写参数并预测（返回带结果的页面）</legend>
          <form action="/ui/predict" method="post" enctype="multipart/form-data">
            <label>选择图像文件（可选；留空则使用下方图像路径）</label>
            <input type="file" name="image" accept="image/*" />

            <div class="row">
              <div>
                <label>或指定图像路径 D1_PATH_IMAGE</label>
                <input type="text" name="D1_PATH_IMAGE" placeholder="test/005091.jpg" />
              </div>
              <div>
                <label>模型路径 M2_PATH_MODEL</label>
                <input type="text" name="M2_PATH_MODEL" value="run/voc11n-seg/weights/best.pt" />
              </div>
            </div>

            <div class="row">
              <div>
                <label>保存目录 D4_FOLDER_PREDICT_SAVE</label>
                <input type="text" name="D4_FOLDER_PREDICT_SAVE" value="out" />
              </div>
              <div>
                <label>预测置信度 P1_PREDICT_CONFIDENCE</label>
                <input type="number" step="0.01" min="0" max="1" name="P1_PREDICT_CONFIDENCE" value="0.25" />
              </div>
            </div>

            <div style="margin-top:12px"><button class="btn" type="submit">开始预测</button></div>
          </form>
        </fieldset>

        <p class=note>提示：预测输出会保存到 D4_FOLDER_PREDICT_SAVE 指定目录。</p>
      </div>
    </div>
  </body>
</html>
"""
        return Response(html, mimetype="text/html")

    @app.route("/ui/predict", methods=["POST"])
    def ui_predict():
        content_type = request.headers.get("Content-Type", "")

        def _read_field(name: str, default: str = "") -> str:
            return str(request.form.get(name, default)).strip()

        img_file = request.files.get("image") if "multipart/form-data" in content_type else None
        model_path = _read_field("M2_PATH_MODEL", "model/best.pt")
        save_dir = _read_field("D4_FOLDER_PREDICT_SAVE", "out")
        conf_text = _read_field("P1_PREDICT_CONFIDENCE", "0.25")
        conf = 0.25
        try:
            conf = float(conf_text)
        except Exception:
            conf = 0.25

        if img_file and getattr(img_file, 'filename', ''):
            p = temp_dir / img_file.filename
            img_file.save(p)
            image_path = str(p)
        else:
            image_path = _read_field("D1_PATH_IMAGE")

        if not image_path:
            return Response("<p style='color:#e33'>未提供图像。请返回上一页上传图片或填写图像路径。</p>", mimetype="text/html", status=400)

        # 运行推理并保存可视化
        try:
            fm = CFunctionModel()
            fm.save_visualization(
                model_path=model_path,
                source=image_path,
                save_dir=save_dir,
                conf=conf,
            )
        except Exception as e:
            return Response(f"<p style='color:#e33'>推理失败：{str(e)}</p>", mimetype="text/html", status=500)

        # 读取原图与预测图并以 base64 嵌入
        try:
            src_name = Path(image_path).name
            pred_path = Path(save_dir) / src_name
            with open(image_path, 'rb') as f:
                orig_b64 = base64.b64encode(f.read()).decode('utf-8')
            with open(pred_path, 'rb') as f:
                pred_b64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            return Response(f"<p style='color:#e33'>读取结果图片失败：{str(e)}</p>", mimetype="text/html", status=500)

        page = f"""
<!doctype html>
<html lang=zh>
<head>
  <meta charset=utf-8 />
  <title>{SOFTWARE_NAME} - 预测结果</title>
  <style>
    :root {{ --bg:#0b1220; --card:#121a2b; --text:#e6e8ef; --muted:#97a0b0; --accent:#4f7cff; --border:#23304a; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial; }}
    .container {{ max-width: 1100px; margin: 32px auto; padding: 0 20px; }}
    .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px; }}
    a.btn {{ text-decoration:none; background: var(--accent); color:#fff; padding:8px 14px; border-radius:10px; font-weight:600; }}
    .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .panel {{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid var(--border); border-radius:14px; padding:14px; }}
    h3 {{ margin: 6px 0 12px; color: var(--muted); font-weight:600; }}
    .img-wrap {{ overflow:hidden; border-radius:12px; border:1px solid var(--border); }}
    img {{ width:100%; display:block; }}
  </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h2>{SOFTWARE_NAME} - 预测结果</h2>
        <a class="btn" href="/ui">返回</a>
      </div>
      <div class="grid">
        <div class="panel">
          <h3>原图</h3>
          <div class="img-wrap"><img src="data:image/jpeg;base64,{orig_b64}" alt="original" /></div>
        </div>
        <div class="panel">
          <h3>预测结果</h3>
          <div class="img-wrap"><img src="data:image/jpeg;base64,{pred_b64}" alt="prediction" /></div>
        </div>
      </div>
    </div>
  </body>
</html>
"""
        return Response(page, mimetype="text/html")

    @app.route("/api/predict", methods=["POST"])
    def api_predict():
        """统一的 HTTP 预测接口。
        支持 multipart/form-data（image/config 或字段）与 application/json。
        与 AFMain.py 相同：最终落地为一个 cfg，然后调用 AFStaff().start(["", cfg]).
        """
        # 1) 解析输入
        content_type = request.headers.get("Content-Type", "")

        def _read_field(name: str, default: str = "") -> str:
            if "application/json" in content_type:
                data = request.get_json(silent=True) or {}
                return str(data.get(name, default)).strip()
            return str(request.form.get(name, default)).strip()

        # 支持上传图片与配置文件
        img_file = request.files.get("image") if "multipart/form-data" in content_type else None
        cfg_file = request.files.get("config") if "multipart/form-data" in content_type else None

        # 字段（若传 config 文件将优先生效）
        img_path_text = _read_field("D1_PATH_IMAGE")
        model_path = _read_field("M2_PATH_MODEL", "model/best.pt")
        save_dir = _read_field("D4_FOLDER_PREDICT_SAVE", "out")
        conf = _read_field("P1_PREDICT_CONFIDENCE", "0.25")
        flow = _read_field("M1_TYPE_FLOW", "0")  # 与 AFMain 一致，0=预测

        # 2) 若上传了 config 文件，直接落地并运行
        if cfg_file and getattr(cfg_file, 'filename', ''):
            cfg_path = temp_dir / cfg_file.filename
            cfg_file.save(cfg_path)
            try:
                staff = AFStaff()
                staff.start(["", str(cfg_path)])
                return jsonify({"status": "ok", "cfg": str(cfg_path)}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # 3) 处理图片上传
        if img_file and getattr(img_file, 'filename', ''):
            p = temp_dir / img_file.filename
            img_file.save(p)
            image_path = str(p)
        else:
            image_path = img_path_text

        if not image_path:
            return jsonify({"error": "未提供图像。请上传图片或填写图像路径。"}), 400

        # 4) 生成临时 cfg 与运行
        cfg_lines = [
            f"D1_PATH_IMAGE={image_path}",
            "D2_TYPE_IMAGE=jpg",
            f"D3_PATH_TRAIN_YAML=",
            f"D4_FOLDER_PREDICT_SAVE={save_dir}",
            f"E1_DIR_EXPORT=run",
            f"M1_TYPE_FLOW={flow}",
            f"M2_PATH_MODEL={model_path}",
            "M3_TYPE_MODEL=0",
            f"P1_PREDICT_CONFIDENCE={conf}",
        ]
        cfg_path = temp_dir / "api_predict.cfg"
        cfg_path.write_text("\n".join(cfg_lines), encoding="utf-8")

        try:
            staff = AFStaff()
            staff.start(["", str(cfg_path)])
            return jsonify({
                "status": "ok",
                "cfg": str(cfg_path),
                "save_dir": save_dir,
                "image": image_path,
                "model": model_path,
                "confidence": conf,
                "flow": flow,
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


