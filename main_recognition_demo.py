#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

import cv2 as cv

from camera.frame_provider import CameraService
from recognizer import close, recognize


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera', default=0)
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=480)
    return parser.parse_args()


def parse_camera(value):
    try:
        return int(value)
    except ValueError:
        return value


def main():
    args = get_args()
    try:
        camera = CameraService(
            camera_id=parse_camera(args.camera),
            width=args.width,
            height=args.height,
        )
    except TypeError:
        camera = CameraService()

    try:
        while True:
            success, frame = camera.read()
            if not success:
                print('Unable to read frame from camera.', flush=True)
                break

            result = recognize(frame)
            if result['label_id'] >= 0:
                print(
                    'Recognized: label_id={}, label={}, score={:.4f}'.format(
                        result['label_id'],
                        result['label'],
                        result['score'],
                    ),
                    flush=True,
                )

            display_text = (
                '{} {:.2f}'.format(result['label'], result['score'])
                if result['label_id'] >= 0
                else 'Unrecognized'
            )
            cv.putText(frame, display_text, (10, 40), cv.FONT_HERSHEY_SIMPLEX,
                       1.0, (0, 255, 0), 2, cv.LINE_AA)
            cv.imshow('GestureRecognizer', frame)

            if cv.waitKey(10) == 27:
                break
    finally:
        camera.release()
        close()
        cv.destroyAllWindows()


if __name__ == '__main__':
    main()
