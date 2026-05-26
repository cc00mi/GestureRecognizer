import argparse
import os

import cv2

from camera.frame_provider import CameraService, preview_camera, probe_camera


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview camera on laptop or Raspberry Pi.")
    parser.add_argument(
        "--camera",
        default="auto",
        help="camera index like 0/1 or device path like /dev/video31; default is auto",
    )
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="run in headless mode and save one captured frame to disk instead of opening a GUI window",
    )
    parser.add_argument(
        "--output",
        default="camera_test.jpg",
        help="output image path used with --no-window",
    )
    args = parser.parse_args()

    if args.camera == "auto":
        camera_index = probe_camera()
        if camera_index is None:
            print("没有探测到可读取图像帧的摄像头设备。")
            print("请先执行: sudo apt install -y v4l-utils")
            print("然后执行: v4l2-ctl --list-devices")
            return
        print(f"已自动选择摄像头: {camera_index}")
    else:
        try:
            camera_index = int(args.camera)
        except ValueError:
            camera_index = args.camera

    camera = CameraService(camera_index=camera_index, width=640, height=480, fps=30)
    if args.no_window:
        success, frame = camera.read()
        camera.release()
        if not success or frame is None:
            print("摄像头已选中，但当前无法读取图像帧。")
            return

        cv2.imwrite(args.output, frame)
        print(f"已成功抓拍一帧并保存到: {os.path.abspath(args.output)}")
        return

    preview_camera(camera)


if __name__ == "__main__":
    main()
