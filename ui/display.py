"""OpenCV display helpers for the sign-recognition UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

import cv2
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None


Color = Tuple[int, int, int]

UNKNOWN_LABEL = "未识别"

# MediaPipe 单手 21 个关键点的骨架连线（拇指/食指/中指/无名指/小指 + 手掌）。
HAND_LANDMARK_COUNT = 21
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)
LANDMARK_COLOR = (0, 220, 255)
CONNECTION_COLOR = (40, 180, 80)

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]


def render(
    frame: np.ndarray,
    result: Optional[Dict[str, Any]],
    fps: Optional[float] = None,
) -> np.ndarray:
    """Draw recognition result on a BGR frame and return the output frame."""

    output = frame.copy()
    result = result or {}
    label = str(result.get("label") or UNKNOWN_LABEL)
    score = _as_float(result.get("score"), default=0.0)
    bbox = result.get("bbox")
    landmarks = result.get("landmarks") or []
    message = str(result.get("message") or "").strip()
    hand_label = str(result.get("handedness") or "").strip()
    gesture_type = str(result.get("type") or "").strip()

    _draw_detection(output, bbox, landmarks)

    is_unknown = label == UNKNOWN_LABEL or score <= 0
    status_color = (70, 70, 220) if is_unknown else (40, 150, 70)
    panel_color = (245, 245, 245)
    text_color = (30, 30, 30)
    panel_height = 132

    cv2.rectangle(output, (0, 0), (output.shape[1], panel_height), panel_color, -1)
    cv2.rectangle(output, (0, panel_height - 3), (output.shape[1], panel_height), status_color, -1)

    title = f"当前识别: {label}"
    confidence = f"置信度: {score:.2f}"
    if fps is not None:
        confidence = f"{confidence}   FPS: {fps:.1f}"
    if hand_label:
        confidence = f"{confidence}   手别: {hand_label}"
    if gesture_type:
        confidence = f"{confidence}   类型: {gesture_type}"

    output = _draw_text(output, title, (18, 16), font_size=30, color=text_color)
    output = _draw_text(output, confidence, (20, 56), font_size=22, color=(80, 80, 80))
    if message:
        output = _draw_text(output, f"状态: {message}", (20, 88), font_size=20, color=(170, 60, 60))

    return output


def _draw_detection(
    frame: np.ndarray,
    bbox: Any,
    landmarks: Iterable[Sequence[float]],
) -> None:
    parsed_bbox = _parse_bbox(bbox)
    if parsed_bbox is not None:
        x1, y1, x2, y2 = parsed_bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), CONNECTION_COLOR, 2)

    points = [
        _parse_point(point, frame.shape[1], frame.shape[0])
        for point in landmarks
    ]

    # 按 21 个点一组拆分（每只手一组），先画骨架连线再画关键点。
    for start in range(0, len(points), HAND_LANDMARK_COUNT):
        hand_points = points[start:start + HAND_LANDMARK_COUNT]
        if len(hand_points) < HAND_LANDMARK_COUNT:
            continue
        for index_a, index_b in HAND_CONNECTIONS:
            point_a = hand_points[index_a]
            point_b = hand_points[index_b]
            if point_a is None or point_b is None:
                continue
            cv2.line(frame, point_a, point_b, CONNECTION_COLOR, 2, cv2.LINE_AA)

    for parsed_point in points:
        if parsed_point is None:
            continue
        cv2.circle(frame, parsed_point, 4, LANDMARK_COLOR, -1, cv2.LINE_AA)
        cv2.circle(frame, parsed_point, 4, (30, 90, 30), 1, cv2.LINE_AA)


def _draw_text(
    frame: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font_size: int,
    color: Color,
) -> np.ndarray:
    if Image is None or ImageDraw is None or ImageFont is None:
        return _draw_text_opencv(frame, text, position, font_size, color)

    font = _load_font(font_size)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb)
    draw = ImageDraw.Draw(image)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)


def _draw_text_opencv(
    frame: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font_size: int,
    color: Color,
) -> np.ndarray:
    ascii_text = text.encode("ascii", errors="replace").decode("ascii")
    scale = max(font_size / 30, 0.5)
    x, y = position
    cv2.putText(
        frame,
        ascii_text,
        (x, y + font_size),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        2,
        cv2.LINE_AA,
    )
    return frame


def _load_font(font_size: int) -> Any:
    for font_path in FONT_CANDIDATES:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, font_size)
    return ImageFont.load_default()


def _parse_bbox(value: Any) -> Optional[Tuple[int, int, int, int]]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None

    try:
        x1, y1, x2, y2 = [int(v) for v in value]
    except (TypeError, ValueError):
        return None

    return x1, y1, x2, y2


def _parse_point(
    point: Sequence[float],
    width: int,
    height: int,
) -> Optional[Tuple[int, int]]:
    if not isinstance(point, (list, tuple)) or len(point) < 2:
        return None

    try:
        x = float(point[0])
        y = float(point[1])
    except (TypeError, ValueError):
        return None

    if 0 <= x <= 1 and 0 <= y <= 1:
        x *= width
        y *= height

    return int(x), int(y)


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
