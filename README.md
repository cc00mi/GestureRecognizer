# GestureRecognizer — 实时手语识别系统

基于 **树莓派 / 电脑摄像头** 的实时中文手语识别系统。使用 MediaPipe 提取双手关键点，通过 TFLite 模型进行动态手势分类，在 OpenCV 窗口中实时显示识别结果。

## 功能特性

- **实时摄像头取帧** — 自动探测摄像头，支持 USB 摄像头和树莓派 CSI 摄像头
- **双手动态手语识别** — 识别 6 类中文手语：你好、再见、对不起、我爱你、没关系、谢谢
- **中文显示界面** — 支持中文字体渲染，显示识别标签、置信度、帧率
- **模型训练流水线** — 提供从视频数据集提取关键点到训练 TFLite 模型的完整脚本

## 项目结构

```
GestureRecognizer/
├── main.py                       # 主程序入口
├── preview_camera.py             # 摄像头预览工具
├── recognizer.py                 # 统一识别接口
├── dynamic_recognizer.py         # 动态手语识别实现
├── extract_dynamic_dataset.py    # 从视频提取双手关键点序列
├── train_dynamic_gesture_classifier.py  # 训练 TFLite 分类模型
├── labels.json                   # 类别标签表
│
├── camera/
│   ├── __init__.py
│   └── frame_provider.py         # 摄像头取帧封装
│
├── model/
│   └── dynamic_gesture_classifier/
│       ├── dynamic_gesture_classifier.py     # TFLite 推理封装
│       ├── dynamic_gesture_classifier.tflite # 预训练模型 (6类)
│       ├── dynamic_gesture_label.csv         # 模型标签
│       └── labels.json
│
├── ui/
│   ├── __init__.py
│   └── display.py                # 识别结果显示渲染
│
├── docs/                         # 设计文档与交付说明
│
├── requirements.txt              # 基础依赖 (运行)
└── requirements-recognition.txt  # 训练依赖
```

## 环境准备

### 安装依赖

```bash
# 推荐使用虚拟环境
python -m venv .venv
source .venv/bin/activate       # Linux
# .venv\Scripts\activate        # Windows

# 基础运行依赖
pip install -r requirements.txt
```

树莓派上如果 `opencv-python` 安装失败，可改用系统包：

```bash
sudo apt update
sudo apt install -y python3-opencv
```

如果需要训练模型，额外安装：

```bash
pip install -r requirements-recognition.txt
```

## 快速使用

### 摄像头预览

```bash
python preview_camera.py              # 自动探测摄像头
python preview_camera.py --camera 0   # 指定设备
python preview_camera.py --no-window --output test.jpg  # 无界面抓拍测试
```

### 运行手语识别

```bash
python main.py
```

其他选项：

```bash
python main.py --camera 0 --width 640 --height 480 --fps 30
```

按 `Q` 或 `ESC` 退出。

### 树莓派 VNC 远程查看

1. 在树莓派上启用 VNC：`sudo raspi-config` → `Interface Options → VNC`
2. 电脑安装 RealVNC Viewer，连接树莓派 IP
3. 在 VNC 终端中运行 `python main.py`

## 演示

> <!-- 演示图片 / 视频链接占位 -->
>
> 运行截图：*（待补充）*
>
> 演示视频：*（待补充）*

## 训练自定义模型

准备视频数据集，按类别分文件夹存放：

```
dataset/
├── 你好/
│   ├── 001.mp4
│   └── 002.mp4
├── 谢谢/
│   └── ...
└── ...
```

提取双手关键点序列：

```bash
python extract_dynamic_dataset.py --dataset dataset --sequence_length 30 --max_num_hands 2
```

训练分类模型：

```bash
python train_dynamic_gesture_classifier.py --epochs 100 --feature_dim 126
```

训练完成后，将 `model/dynamic_gesture_classifier/dynamic_gesture_classifier.tflite` 替换即可生效。

当前模型训练效果：

| 指标 | 数值 |
|------|------|
| 有效样本 | 139 |
| 训练准确率 | 0.9732 |
| 验证准确率 | 0.7778 |

## 技术栈

- **Python 3** — 主开发语言
- **MediaPipe** — 手部关键点检测
- **TensorFlow Lite** — 端侧推理
- **OpenCV** — 摄像头取帧与画面渲染
- **Pillow** — 中文字体渲染

## 许可证

本项目仅供学习交流使用。
