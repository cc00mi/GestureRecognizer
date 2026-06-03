# PR 标题

接入 2 号同学动态双手手语识别模块

# PR 正文

## 改动内容

- 新增 `recognizer.py`，按仓库协作约定提供 `recognize(frame)` 接口。
- 新增 `dynamic_recognizer.py`，实现基于 MediaPipe 的双手动态手语识别。
- 新增 `model/dynamic_gesture_classifier/`，包含 TFLite 分类器、标签文件和已训练模型。
- 新增 `extract_dynamic_dataset.py` 和 `train_dynamic_gesture_classifier.py`，支持从分类视频目录提取双手关键点并训练模型。
- 新增 `main_recognition_demo.py`，演示如何和 1 号同学的 `camera.frame_provider.CameraService` 对接。
- 新增 `README_2_recognition.md` 和 `docs/2号同学交付说明.md`，说明接口、训练流程和当前模型效果。

## 对接方式

4 号同学或主程序只需要调用：

```python
from recognizer import recognize

result = recognize(frame)
```

返回格式：

```python
{
    "label_id": 0,
    "label": "你好",
    "score": 0.93,
    "type": "dynamic"
}
```

未稳定识别时返回：

```python
{
    "label_id": -1,
    "label": "未识别",
    "score": 0.0,
    "type": "dynamic"
}
```

## 当前支持类别

- 你好
- 再见
- 对不起
- 我爱你
- 没关系
- 谢谢

## 模型说明

- 使用双手动态关键点序列。
- 每帧特征为 `Left 63维 + Right 63维 = 126维`。
- 每个动作序列为 30 帧。
- TFLite 输入形状：`[1, 30, 126]`。
- TFLite 输出形状：`[1, 6]`。

## 验证

- 已在本地通过 Python 编译检查。
- 当前训练集有效样本 139，跳过 2。
- 训练准确率 0.9732，验证准确率 0.7778。
- 离线测试 `你好.mp4` 预测为 `你好`，置信度约 0.9175。
- `我爱你` 类别离线检查：20 个样本中 19 个识别正确。

## 依赖说明

需要安装：

```text
opencv-python
mediapipe
numpy
tensorflow
```

树莓派上如果 `opencv-python` 安装失败，可以继续使用仓库 README 中说明的 `python3-opencv`。
