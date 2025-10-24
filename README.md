项目环境创建与运行指南

一、使用 Conda（推荐）
1) 创建并激活环境（Python 3.10）
conda create -n irisseg python=3.10 -y
conda activate irisseg

2) 设置语言（兼容含中文路径）
export LANG=C.UTF-8 LC_ALL=C.UTF-8

3) 进入项目并安装依赖
cd /Users/qipengfei/Desktop/深度学习_期末考试
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt

4) 安装 PyTorch
- macOS（CPU）：
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
- 服务器 CUDA 11.8：
pip install --index-url https://download.pytorch.org/whl/cu118 torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0

5) 验证安装
python -c "import torch;print('cuda', torch.cuda.is_available());import ultralytics;print('ultralytics', ultralytics.__version__)"

二、使用 venv（如不使用 Conda）
python3.10 -m venv .venv
source .venv/bin/activate
export LANG=C.UTF-8 LC_ALL=C.UTF-8
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
# 安装与上面相同的 PyTorch 指令（根据平台二选一）

三、运行
# 预测（编辑 VOC_config.txt 填好模型/图片路径）
python AFMain.py VOC_config.txt

四、常见问题排查
1) 确认解释器与 pip 属于同一环境：
which python
python -V
python -m pip -V
python -c "import sys;print(sys.executable)"

2) 核心包自检：
python -c "import ultralytics,cv2,numpy,flask;print('ok')"

3) VS Code 选择解释器：命令面板 → Python: Select Interpreter → 选择 irisseg 或 .venv