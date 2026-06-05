import time
from typing import Optional, Tuple, Union

import cv2
import numpy as np


class CameraService:
    """Simple camera wrapper for Raspberry Pi or laptop USB cameras."""

    def __init__(
        self,
        camera_index: Union[int, str] = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
    ) -> None:
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        if self.cap is not None and self.cap.isOpened():
            return True

        # URL 流不能指定 V4L2/Linux 后端；Windows 也不支持
        if isinstance(self.camera_index, str):
            self.cap = cv2.VideoCapture(self.camera_index)
        else:
            self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        return True

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.open():
            return False, None
        success, frame = self.cap.read()
        if not success:
            return False, None
        return True, frame

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None


_default_camera = CameraService()


def get_frame() -> Tuple[bool, Optional[np.ndarray]]:
    """
    返回:
        success: bool
        frame: np.ndarray  # BGR 格式图像
    """
    return _default_camera.read()


def preview_camera(camera: Optional[CameraService] = None, window_name: str = "Camera Preview") -> None:
    camera = camera or _default_camera
    last_time = time.time()

    while True:
        success, frame = camera.read()
        if not success or frame is None:
            print("无法读取摄像头画面，请检查摄像头连接或 camera_index。")
            break

        current_time = time.time()
        fps = 1.0 / max(current_time - last_time, 1e-6)
        last_time = current_time

        cv2.putText(
            frame,
            f"Camera OK | FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


def probe_camera(
    candidates: Optional[list[Union[int, str]]] = None,
    width: int = 640,
    height: int = 480,
    fps: int = 30,
) -> Optional[Union[int, str]]:
    """
    依次尝试候选摄像头设备，返回第一个真正能读出图像帧的设备。
    """
    if candidates is None:
        candidates = [0, 1, 2, 3] + [f"/dev/video{i}" for i in range(0, 32)]

    for candidate in candidates:
        camera = CameraService(candidate, width=width, height=height, fps=fps)
        success, frame = camera.read()
        camera.release()
        if success and frame is not None:
            return candidate
    return None
