import cv2

from camera.frame_provider import CameraService, probe_camera


def mock_recognize(frame):
    """
    这是给 1 号同学联调用的占位识别结果。
    真正接入时由 2 号同学替换成 recognize(frame)。
    """
    height, width = frame.shape[:2]
    return {
        "label_id": -1,
        "label": "未识别",
        "score": 0.0,
        "handedness": "Unknown",
        "bbox": [0, 0, width, height],
        "landmarks": [],
    }


def render(frame, result):
    """
    这是给 1 号同学联调用的占位界面逻辑。
    真正接入时由 4 号同学替换成 render(frame, result)。
    """
    output = frame.copy()
    text = f"当前识别: {result['label']} ({result['score']:.2f})"
    cv2.putText(
        output,
        text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return output


def main() -> None:
    camera_index = probe_camera()
    if camera_index is None:
        print("没有探测到可读取图像帧的摄像头设备，请先运行 preview_camera.py 排查。")
        return

    camera = CameraService(camera_index=camera_index, width=640, height=480, fps=30)

    while True:
        success, frame = camera.read()
        if not success or frame is None:
            print("无法读取摄像头画面，请检查设备连接。")
            break

        result = mock_recognize(frame)
        output = render(frame, result)
        cv2.imshow("Sign Recognition Demo", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
