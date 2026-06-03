"""Final integration entry for the sign-recognition demo."""

from __future__ import annotations

import argparse
import time
from typing import Optional

import cv2
import numpy as np

from camera.frame_provider import CameraService, probe_camera
import recognizer as recognizer_module
from ui.display import render


WINDOW_NAME = "Sign Recognition Demo"


def main() -> None:
    args = parse_args()
    camera_index = _camera_source(args.camera, args.width, args.height, args.fps)
    if camera_index is None:
        _show_error("未检测到可用摄像头", args.width, args.height)
        return

    camera = CameraService(camera_index=camera_index, width=args.width, height=args.height, fps=args.fps)
    last_time = time.perf_counter()
    current_fps: Optional[float] = None

    try:
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                frame = _blank_frame(args.width, args.height)
                result = {"label": "未识别", "score": 0.0, "message": "摄像头读取失败"}
            else:
                result = recognizer_module.recognize(frame)

            now = time.perf_counter()
            elapsed = now - last_time
            last_time = now
            if elapsed > 0:
                instant_fps = 1.0 / elapsed
                current_fps = instant_fps if current_fps is None else current_fps * 0.85 + instant_fps * 0.15

            output = render(frame, result, fps=current_fps)
            cv2.imshow(WINDOW_NAME, output)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    finally:
        camera.release()
        _close_recognizer()
        cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sign recognition display UI")
    parser.add_argument("--camera", default="auto", help="Camera index, video path, or auto. Default: auto")
    parser.add_argument("--width", type=int, default=640, help="Capture width. Default: 640")
    parser.add_argument("--height", type=int, default=480, help="Capture height. Default: 480")
    parser.add_argument("--fps", type=int, default=30, help="Target capture FPS. Default: 30")
    return parser.parse_args()


def _camera_source(value: int | str, width: int, height: int, fps: int) -> Optional[int | str]:
    if isinstance(value, int):
        return value

    normalized = value.strip().lower()
    if normalized == "auto":
        return probe_camera(width=width, height=height, fps=fps)

    return int(value) if value.isdigit() else value


def _blank_frame(width: int, height: int) -> np.ndarray:
    return np.full((height, width, 3), 235, dtype=np.uint8)


def _show_error(message: str, width: int, height: int) -> None:
    frame = _blank_frame(width, height)
    result = {"label": "未识别", "score": 0.0, "message": message}
    output = render(frame, result)
    cv2.imshow(WINDOW_NAME, output)

    while True:
        key = cv2.waitKey(50) & 0xFF
        if key in (27, ord("q")):
            break

    cv2.destroyAllWindows()


def _close_recognizer() -> None:
    close_func = getattr(recognizer_module, "close", None)
    if callable(close_func):
        close_func()


if __name__ == "__main__":
    main()
