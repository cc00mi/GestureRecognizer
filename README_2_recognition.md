# 2号同学：动态手语识别模块接入说明

本次提交补充 2 号同学负责的识别模块，按仓库 README 约定提供：

```python
from recognizer import recognize

result = recognize(frame)
```

`frame` 使用 1 号同学提供的 `camera.frame_provider` 摄像头帧，格式为 OpenCV BGR `np.ndarray`。

## 返回格式

识别成功：

```python
{
    "label_id": 0,
    "label": "你好",
    "score": 0.93,
    "type": "dynamic"
}
```

未稳定识别到完整动作：

```python
{
    "label_id": -1,
    "label": "未识别",
    "score": 0.0,
    "type": "dynamic"
}
```

## 当前类别

- 你好
- 再见
- 对不起
- 我爱你
- 没关系
- 谢谢

## 模型说明

当前模型是双手动态手语模型：

- 每帧使用 `Left 63维 + Right 63维 = 126维`
- 每个动作序列使用 30 帧
- TFLite 输入形状为 `[1, 30, 126]`
- TFLite 输出形状为 `[1, 6]`

模型文件：

```text
model/dynamic_gesture_classifier/dynamic_gesture_classifier.tflite
model/dynamic_gesture_classifier/dynamic_gesture_label.csv
model/dynamic_gesture_classifier/labels.json
```

## 运行演示

在仓库虚拟环境中安装依赖后：

```powershell
python main_recognition_demo.py --camera 0
```

Linux / Raspberry Pi：

```bash
python3 main_recognition_demo.py --camera 0
```

如果 4 号同学已经实现 `render(frame, result)`，主流程可按接口文档整合：

```python
success, frame = camera.read()
result = recognize(frame)
output = render(frame, result)
```

## 训练命令

视频数据集结构：

```text
dataset/
  你好/
    001.mp4
  谢谢/
    001.mp4
```

提取双手关键点：

```powershell
python extract_dynamic_dataset.py --dataset dataset --sequence_length 30 --max_num_hands 2
```

训练模型：

```powershell
python train_dynamic_gesture_classifier.py --epochs 100 --feature_dim 126
```

## 依赖

需要在 `requirements.txt` 中包含或安装：

```text
opencv-python
mediapipe
numpy
tensorflow
```

树莓派如果安装 `opencv-python` 失败，仍可按仓库 README 使用系统 `python3-opencv`。
