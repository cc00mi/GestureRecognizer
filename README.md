# GestureRecognizer_v0.1

基于树莓派和摄像头的固定手势识别系统项目仓库。

当前仓库先完成了 1 号负责的基础部分：

- 树莓派摄像头环境跑通
- 统一摄像头取帧接口
- 摄像头实时预览脚本
- 供 2 号、4 号同学联调的最小主程序

## 当前目录结构

```text
GestureRecognizer/
  camera/
    __init__.py
    frame_provider.py
  main.py
  preview_camera.py
  requirements.txt
  README.md
  技术方案.md
  接口文档.md
```

## 环境准备

建议在本地自行创建虚拟环境，不要把虚拟环境提交到 GitHub。

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / Raspberry Pi

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果树莓派上 `opencv-python` 安装失败，可以改用系统包：

```bash
sudo apt update
sudo apt install -y python3-opencv
```

## 依赖安装

```bash
pip install -r requirements.txt
```

## 摄像头预览

### 自动探测并打开实时预览

```bash
python3 preview_camera.py
```

### 手动指定摄像头

```bash
python3 preview_camera.py --camera 0
```

或者：

```bash
python3 preview_camera.py --camera /dev/video0
```

### 无图形桌面时抓拍测试

```bash
python3 preview_camera.py --camera 0 --no-window --output test.jpg
```

## 树莓派通过 VNC 查看实时画面

实测可用的操作方式如下：

1. 执行：

```bash
sudo raspi-config
```

2. 进入：

`Advanced Options -> Wayland -> X11`

`display->4Dp60nHDMI`

`Interface Options -> VNC `

3. 在电脑上安装并打开 `RealVNC Viewer`

4. 在树莓派上查看 IP：

```bash
hostname -I
```

5. 测试：用电脑连接树莓派桌面后，在终端执行

```bash
source .venv/bin/activate
python3 preview_camera.py
```

可看到实时显示画面

如果项目不在 `.venv` 环境中，请按实际环境激活

## 给组员的接口说明

### 摄像头取帧接口

```python
from camera.frame_provider import CameraService, get_frame

camera = CameraService()
success, frame = camera.read()
```

或者：

```python
success, frame = get_frame()
```

约定：

- `frame` 类型：`np.ndarray`
- 图像格式：`OpenCV BGR`
- 建议分辨率：`640x480`
- 目标帧率：`15~30 FPS`

## 后续协作建议

- 2 号同学实现 `recognize(frame)`
- 3 号同学补充 `labels.json` 和样本数据
- 4 号同学实现 `render(frame, result)`
- 1 号同学负责最终树莓派实机联调
