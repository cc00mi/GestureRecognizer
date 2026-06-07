# GestureRecognizer — 实时动态手语识别系统

基于 **MediaPipe Hands** + **TensorFlow Lite / ai-edge-litert** 的实时动态手语识别系统，支持 10 种中文手语词，专为树莓派与 PC 双平台部署设计。

## 演示视频

> 🎥 https://www.bilibili.com/video/BV15mE86tEui/?spm_id_from=333.1387.homepage.video_card.click
>

## 快速开始

### 1. 环境准备

**电脑端 (Windows / Linux / macOS):**

```bash
cd GestureRecognizer
pip install -r requirements.txt
```

**树莓派 (Raspberry Pi):**

```bash
# 系统依赖
sudo apt-get update

# 安装系统编译依赖
sudo apt install build-essential libssl-dev zlib1g-dev libncurses5-dev \
                 libreadline-dev libsqlite3-dev libgdbm-dev libbz2-dev \
                 liblzma-dev tk-dev libffi-dev wget -y

# 下载编译 Python 3.8.18（稳定版）
wget https://www.python.org/ftp/python/3.8.18/Python-3.8.18.tgz
tar -zxvf Python-3.8.18.tgz
cd Python-3.8.18
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall

# 中文字体
sudo apt-get install fonts-wqy-microhei -y

# 创建并进入虚拟环境
python3.8 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 启动识别

```bash
python main.py
```

### 树莓派远程查看

树莓派通过 VNC 查看实时画面：

1. 启用 VNC：

```bash
sudo raspi-config
# → Interface Options → VNC → Enable
# → Display Options → VNC Resolution → 1280*720  → Enable
# → Finish → reboot
```

2. 在电脑上安装并打开 `RealVNC Viewer`
3. 查看树莓派 IP：

```bash
hostname -I
```

4. 连接 VNC 后在终端中执行：

```bash
python main.py
```

## 项目架构

```
GestureRecognizer/
│
├── main.py                         ← 程序入口
├── recognizer.py                   ← 识别接口
├── dynamic_recognizer.py           ← 手语识别引擎
├── labels.json                     ← 静态标签映射
│
├── camera/
│   ├── __init__.py
│   └── frame_provider.py           ← 摄像头驱动
│
├── model/
│   ├── __init__.py
│   └── dynamic_gesture_classifier/
│       ├── __init__.py
│       ├── dynamic_gesture_classifier.py    ← TFLite 推理封装
│       ├── dynamic_gesture_classifier.tflite ← 部署模型
│       ├── dynamic_gesture_classifier.h5     ← 训练权重
│       └── dynamic_gesture_label.csv        ← 类别标签
│
├── ui/
│   ├── __init__.py
│   └── display.py                  ← 画面渲染
│
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## 数据流

```
┌──────────────┐
│  摄像头 / USB │  每帧 BGR 图像 (支持 RTSP / HTTP 网络流)
│  自动探测索引  │
└──────┬───────┘
       ▼
┌──────────────┐
│  MediaPipe   │  检测手部 21 个关键点 (x, y, z)
│    Hands     │  归一化 + 零中心化 → 126 维特征 (左手63D + 右手63D)
└──────┬───────┘
       │ 收集 30 帧
       ▼
┌──────────────────────┐
│  DynamicGestureClassifier  │  Conv1D 时序卷积网络
│  输入: [1, 30, 126]       │  11 类 softmax 输出
│  推理: TFLite              │  兼容 ai-edge-litert (树莓派) / tf.lite (PC)
└──────┬─────────────────┘
       │ (label_id, score)
       ▼
┌──────────────┐
│  稳定过滤     │  连续 8 次预测一致 + 置信度 > 0.25 → 输出
│  (stable_count) │  否则保持"未识别"状态
└──────┬───────┘
       ▼
┌──────────────┐
│  OpenCV 显示  │  PIL 渲染中文 + 手部骨架 (21 点连线)
│  可拖拽窗口    │  实时 FPS 显示 + 置信度 + 识别结果
└──────────────┘
```

## 模型架构

```
Input: (None, 30, 126)
  │
  ├─ Conv1D(64) → BN → ReLU → Conv1D(64) → BN → ReLU → MaxPool → Dropout(0.3)
  ├─ Conv1D(128) → BN → ReLU → Conv1D(128) → BN → ReLU → MaxPool → Dropout(0.3)
  ├─ Conv1D(256) → BN → ReLU → GlobalAveragePooling1D → Dropout(0.4)
  ├─ Dense(128, L2 正则化) → Dropout(0.4)
  └─ Dense(11, softmax)
       │
Output: 你好 / 再见 / 对不起 / 没关系 / 谢谢 /
        上课 / 下课 / 不舒服 / 厉害 / 多少钱
```

### 特征提取

每帧两手各产出 21 个关键点 (x, y, z)，经**零中心化**（以腕部点 0 为基准）和**最大绝对值归一化**后拼接为 126 维特征向量。系统累计 30 帧构成一个时序窗口输入模型。

## 支持的手语词 (10 类)

| ID   | 手语词 | 说明             |
| ---- | ------ | ---------------- |
| 1    | 你好   | Hello            |
| 2    | 再见   | Goodbye          |
| 3    | 对不起 | Sorry            |
| 4    | 没关系 | It's okay        |
| 5    | 谢谢   | Thank you        |
| 6    | 上课   | Class begins     |
| 7    | 下课   | Class ends       |
| 8    | 不舒服 | Not feeling well |
| 9    | 厉害   | Amazing          |
| 10   | 多少钱 | How much         |

## 识别灵敏度调整

`dynamic_recognizer.py` 中几个关键参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `score_threshold` | 0.6 | 置信度阈值 (0~1, 越低越敏感但可能误判) |
| `stable_count` | 10 | 连续多少帧预测一致才确认输出（越低越敏感但可能误判） |

另外在 `recognizer.py` 的 `init()` 中可通过 `model_complexity` 参数 (0/1/2) 控制 MediaPipe 模型复杂度，值越大精度越高但速度越慢。 

## 模型性能

| 指标 | 值 |
|------|-----|
| 训练样本 | 434 (原始 139 + 自采集 295) |
| 增强后训练集 | 2,604 |
| 验证准确率 | **96.51%** |
| 类别数 | 10 |
| TFLite 大小 | 1.7 MB |

### 每类精度

| 手势   | Precision | Recall | F1    |
|--------|-----------|--------|-------|
| 你好   | 1.00      | 1.00   | 1.00  |
| 再见   | 1.00      | 0.80   | 0.89  |
| 对不起 | 1.00      | 0.88   | 0.93  |
| 没关系 | 0.86      | 0.86   | 0.86  |
| 谢谢   | 1.00      | 1.00   | 1.00  |
| 上课   | 0.88      | 1.00   | 0.93  |
| 下课   | 1.00      | 1.00   | 1.00  |
| 不舒服 | 0.86      | 1.00   | 0.92  |
| 厉害   | 1.00      | 1.00   | 1.00  |
| 多少钱 | 1.00      | 1.00   | 1.00  |

## 未来可做

### 🔹 树莓派集成屏幕 — 更轻便化

将系统部署到树莓派 + 小型触摸屏（如 5 英寸 HDMI 显示屏）上，实现一体化的离线手语识别终端。摆脱对 PC 或 VNC 远程桌面的依赖，成为一个真正的**便携式手语翻译设备**，适用于课堂、医院、服务窗口等场景。

### 🔹 扩大数据集 — 覆盖更多日常词汇

当前系统支持 10 个日常手语词，未来计划：
- 扩充至 50+ 常用词汇（涵盖数字、时间、方向、情感等）
- 引入更多手语使用者的真实采集数据，提升泛化能力
- 建立开放的手语数据集，推动中文手语识别社区发展

### 🔹 实时手语翻译 — 从词到句

当前系统识别孤立词，未来演进方向：
- **连续手语识别**：利用 Seq2Seq / Transformer 模型，将连续手语动作流直接翻译为自然语句
- **端到端翻译**：结合大语言模型 (LLM) 对识别结果进行语义理解和语法修正
- **双向交互**：将文本/语音反向合成为手语动画，实现手语 ↔ 自然语言的完整闭环

### 🔹 边缘计算优化

- 基于 `ai-edge-litert` 进一步利用树莓派的 GPU / NPU（如 Raspberry Pi AI Kit）加速推理
- 模型量化和剪枝，在保持精度的同时将模型体积压缩至 1 MB 以下
- 探索 MediaPipe Tasks 新版本 API，降低延迟提升帧率

### 🔹 多平台应用

- 移动端移植：通过 TensorFlow Lite 部署至 Android / iOS
- Web 端演示：使用 TensorFlow.js 在浏览器中运行轻量版
- 嵌入式设备：适配 RV1126 / RK3588 等边缘计算平台

## 许可证

本项目基于 MIT 许可证开源，详情参见 LICENSE 文件。
