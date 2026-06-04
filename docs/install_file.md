1. 安装库
```
mediapipe==0.10.5
OpenCV 4.5.1
TensorFlow 2.10.0
scikit-learn 0.23.2
matplotlib 3.3.2
numpy 1.23.5
h5py: 3.7.0
protobuf 3.20.3
```

2. 版本较老，需要python3.8
`winget install --id Python.Python.3.8 -e`

3. 创建虚拟环境
```
py -3.8 -m venv .venv38
.\.venv38\Scripts\Activate.ps1
python --version
```
4. 装依赖
```
python -m pip install --upgrade pip setuptools wheel
python -m pip install numpy==1.18.5 protobuf==3.20.3
python -m pip install mediapipe==0.10.5
python -m pip install opencv-contrib-python==4.5.1.48
python -m pip install tensorflow==2.3.0
python -m pip install scikit-learn==0.23.2 matplotlib==3.3.2
```
5. 运行
```
.\hgr38\Scripts\Activate.ps1
python app.py --device 0 --backend any --width 640 --height 480
```