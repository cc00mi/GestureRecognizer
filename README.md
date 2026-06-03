# GestureRecognizer_v0.1

基于树莓派和摄像头的固定手势识别系统项目仓库。

当前仓库已完成 1 号摄像头基础部分，并接入 4 号显示界面：

- 树莓派摄像头环境跑通
- 统一摄像头取帧接口
- 摄像头实时预览脚本
- 最终集成主程序显示摄像头画面、识别结果、置信度和 FPS

## 当前目录结构

```text
GestureRecognizer/
  camera/
    __init__.py
    frame_provider.py
  ui/
    __init__.py
    display.py
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

## 最终显示界面

默认自动探测摄像头，并显示 2 号识别接口返回的中文结果：

```bash
python3 main.py
```

手动指定摄像头或视频路径：

```bash
python3 main.py --camera 0
python3 main.py --camera /dev/video0
```

按 `q` 或 `Esc` 退出。

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

### 显示界面接口

```python
from ui.display import render

output = render(frame, result, fps=25.0)
```

`result` 至少包含：

```python
{
    "label": "谢谢",
    "score": 0.92
}
```

如果 2 号识别接口返回 `bbox`、`landmarks`、`handedness` 或 `type`，界面会自动显示。

## 后续协作建议

- 2 号同学实现 `recognize(frame)`
- 3 号同学补充 `labels.json` 和样本数据
- 4 号同学已实现 `render(frame, result)` 并接入 `main.py`
- 1 号同学负责最终树莓派实机联调
