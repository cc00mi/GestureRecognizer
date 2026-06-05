# GestureRecognizer — 实时动态手语识别系统

基于 MediaPipe + TensorFlow Lite 的**实时动态手语识别**，支持 11 种中文手语词，专为树莓派部署设计。

---

## 项目架构

```
GestureRecognizer/
│
├── main.py                         ← 程序入口 (摄像头 → 识别 → 显示)
├── recognizer.py                   ← 识别接口封装 (threshold=0.25, stable=8)
├── dynamic_recognizer.py           ← 手语识别引擎 (30帧序列 → Conv1D → 11类)
│
├── camera/
│   ├── __init__.py
│   └── frame_provider.py           ← 摄像头驱动 (本地 / RTSP / HTTP)
│
├── ui/
│   ├── __init__.py
│   └── display.py                  ← 画面渲染 (PIL 中文 + 手部骨架 + 信息面板)
│
├── model/
│   ├── __init__.py
│   └── dynamic_gesture_classifier/
│       ├── __init__.py
│       ├── dynamic_gesture_classifier.py    ← TFLite 推理封装
│       ├── dynamic_gesture_classifier.tflite ← 部署模型 (1.7 MB, 11类)
│       ├── dynamic_gesture_classifier.h5     ← 训练权重 (可继续训练)
│       └── dynamic_gesture_label.csv        ← 11 个类别标签
│
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## 数据流

```
┌──────────────┐
│  摄像头/USB   │  每帧 BGR 图像
└──────┬───────┘
       ▼
┌──────────────┐
│  MediaPipe   │  检测手部 21 个关键点
│    Hands     │  提取 126 维特征 (左手63D + 右手63D)
└──────┬───────┘
       │ 收集 30 帧
       ▼
┌──────────────────────┐
│  DynamicGestureClassifier  │  Conv1D 时序卷积网络
│  输入: [1, 30, 126]       │  11 类 softmax 输出
└──────┬───────────────┘
       │ (label_id, score)
       ▼
┌──────────────┐
│  稳定过滤     │  连续 8 次预测一致 + 置信度 > 0.25 → 输出
└──────┬───────┘
       ▼
┌──────────────┐
│  OpenCV 显示  │  PIL 渲染中文 + 手部骨架 + 识别结果
└──────────────┘
```

---

## 模型架构

```
Input: (None, 30, 126)
  │
  ├─ Conv1D(64) → BN → ReLU → Conv1D(64) → BN → ReLU → MaxPool → Dropout(0.3)
  ├─ Conv1D(128) → BN → ReLU → Conv1D(128) → BN → ReLU → MaxPool → Dropout(0.3)
  ├─ Conv1D(256) → BN → ReLU → GlobalAveragePooling1D → Dropout(0.4)
  ├─ Dense(128, L2正则化) → Dropout(0.4)
  └─ Dense(11, softmax)
       │
Output: 你好 / 再见 / 对不起 / 我爱你 / 没关系 / 谢谢 /
        上课 / 下课 / 不舒服 / 厉害 / 多少钱
```

---

## 支持的手语词 (11 类)

| ID | 手语词 | 说明 |
|----|--------|------|
| 0  | 你好    | Hello |
| 1  | 再见    | Goodbye |
| 2  | 对不起   | Sorry |
| 3  | 我爱你   | I love you |
| 4  | 没关系   | It's okay |
| 5  | 谢谢    | Thank you |
| 6  | 上课    | Class begins |
| 7  | 下课    | Class ends |
| 8  | 不舒服   | Not feeling well |
| 9  | 厉害    | Amazing |
| 10 | 多少钱   | How much |

---

## 快速开始

### 1. 环境准备

**电脑端 (Windows/Linux/macOS):**

```bash
cd GestureRecognizer
pip install -r requirements.txt
```

**树莓派:**

```bash
# 系统依赖
sudo apt-get update
sudo apt-get install python3-opencv python3-pil python3-numpy -y

# 中文字体
sudo apt-get install fonts-wqy-microhei -y

# Python 包
pip install tflite-runtime mediapipe-rpi4 scikit-learn
```

### 2. 启动识别

```bash
# 本地 USB 摄像头 (自动探测)
python main.py --camera auto

# 指定设备
python main.py --camera 0 --width 640 --height 480

# 树莓派 CSI 摄像头
sudo modprobe bcm2835-v4l2
python main.py --camera /dev/video0

# RTSP 网络流
python main.py --camera rtsp://192.168.1.100:8554/stream
```

按 `Q` 或 `ESC` 退出。

---

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--camera` | auto | 摄像头: `auto` / 数字 / `/dev/video0` / `rtsp://...` |
| `--width` | 640 | 画面宽度 |
| `--height` | 480 | 画面高度 |
| `--fps` | 30 | 目标帧率 |

---

## 识别灵敏度调整

`recognizer.py` 和 `dynamic_recognizer.py` 中两个关键参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `score_threshold` | 0.25 | 置信度阈值 (0~1, 越低越敏感但可能误判) |
| `stable_count` | 8 | 连续多少帧预测一致才确认输出 |

---

## 模型性能

| 指标 | 值 |
|------|-----|
| 训练样本 | 434 (原始139 + 自采集295) |
| 增强后训练集 | 2,604 |
| 验证准确率 | **96.51%** |
| 类别数 | 11 |
| TFLite 大小 | 1.7 MB |

### 每类精度

| 手势 | Precision | Recall | F1 |
|------|-----------|--------|-----|
| 你好 | 1.00 | 1.00 | 1.00 |
| 再见 | 1.00 | 0.80 | 0.89 |
| 对不起 | 1.00 | 0.88 | 0.93 |
| 我爱你 | 1.00 | 1.00 | 1.00 |
| 没关系 | 0.86 | 0.86 | 0.86 |
| 谢谢 | 1.00 | 1.00 | 1.00 |
| 上课 | 0.88 | 1.00 | 0.93 |
| 下课 | 1.00 | 1.00 | 1.00 |
| 不舒服 | 0.86 | 1.00 | 0.92 |
| 厉害 | 1.00 | 1.00 | 1.00 |
| 多少钱 | 1.00 | 1.00 | 1.00 |

---

## 依赖

```
python >= 3.8
 依赖清单

  运行时 (必须)

  ┌───────────────┬────────┬────────────────────────────────────┐
  │     包名      │  版本  │                用途                │
  ├───────────────┼────────┼────────────────────────────────────┤
  │ numpy         │ 1.23.5 │ 数组运算、特征矩阵                 │
  ├───────────────┼────────┼────────────────────────────────────┤
  │ opencv-python │ 4.5.1  │ 摄像头取帧 + 画面渲染              │
  ├───────────────┼────────┼────────────────────────────────────┤
  │ mediapipe     │ 0.10.5 │ 手部 21 关键点检测                 │
  ├───────────────┼────────┼────────────────────────────────────┤
  │ Pillow        │ 10.4.0 │ 中文文字渲染 (树莓派: python3-pil) │
  └───────────────┴────────┴────────────────────────────────────┘

  推理引擎 (二选一)

  ┌────────────────────┬────────────────┬────────┐
  │        平台        │      包名      │  版本  │
  ├────────────────────┼────────────────┼────────┤
  │ PC (Windows/Linux) │ tensorflow     │ 2.10.1 │
  ├────────────────────┼────────────────┼────────┤
  │ 树莓派 (ARM)       │ tflite-runtime │ 2.14.0 │
  └────────────────────┴────────────────┴────────┘

  可选 (训练/评估)

  ┌──────────────┬────────┬────────────────────┐
  │     包名     │  版本  │        用途        │
  ├──────────────┼────────┼────────────────────┤
  │ scikit-learn │ 0.23.2 │ 训练时打印分类报告 │
  ├──────────────┼────────┼────────────────────┤
  │ matplotlib   │ 3.3.2  │ 训练时显示实时曲线 │
  └──────────────┴────────┴────────────────────┘

  树莓派补充

  ┌─────────────────────────────────────────────┬──────────────────────┐
  │                  安装方式                   │         说明         │
  ├─────────────────────────────────────────────┼──────────────────────┤
  │ sudo apt install fonts-wqy-microhei         │ 中文字体             │
  ├─────────────────────────────────────────────┼──────────────────────┤
  │ sudo apt install python3-opencv python3-pil │ 系统包版更快         │
  ├─────────────────────────────────────────────┼──────────────────────┤
  │ pip install mediapipe-rpi4                  │ 树莓派专用 MediaPipe │
  └─────────────────────────────────────────────┴──────────────────────┘

  ---
  requirements.txt 已更新，PC 端直接 pip install -r requirements.txt 即可。树莓派端把 tensorflow
  行注释掉，换 tflite-runtime。

---

## License

Apache License 2.0
