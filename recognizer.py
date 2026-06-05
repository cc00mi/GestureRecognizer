#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dynamic_recognizer import DynamicHandGestureRecognizer


_default_recognizer = None


def recognize(frame):
    """
    Recognize a dynamic sign language gesture from one OpenCV BGR frame.

    Args:
        frame: np.ndarray, BGR image returned by camera.frame_provider.

    Returns:
        dict with label_id, label, score, and type fields.
    """
    global _default_recognizer
    if _default_recognizer is None:
        _default_recognizer = DynamicHandGestureRecognizer(
            score_threshold=0.35,
            stable_count=20,
        )
    return _default_recognizer.recognize(frame)


def close():
    global _default_recognizer
    if _default_recognizer is not None:
        _default_recognizer.close()
        _default_recognizer = None
