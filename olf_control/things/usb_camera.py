import cv2 as cv
import numpy as np


class USBCamera:
    """PiCamera API compatible wrapper over opencv camera.

    Note that only the necessary methods for this project
    are implemented
    """

    def __init__(self, idx=0):

        self.device_idx = idx
        self._camera = cv.VideoCapture(idx)
        self.hflip = False
        self.vflip = False
        self.zoom = (0.0, 0.0, 1.0, 1.0)

    def __enter__(self):
        if self.closed:
            self._camera = cv.VideoCapture(self.device_idx)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._camera.release()

    @property
    def resolution(self):
        return [
            int(self._camera.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(self._camera.get(cv.CAP_PROP_FRAME_HEIGHT)),
        ]

    @resolution.setter
    def resolution(self, resolution):
        print(f"setting resolution to ({resolution}) in core camera")

        width, height = resolution
        self._camera.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self._camera.set(cv.CAP_PROP_FRAME_HEIGHT, height)

    @property
    def closed(self):
        return not self._camera.isOpened()

    def read(self):
        check, frame = self._camera.read()
        if not check:
            return None

        if self.vflip:
            frame = frame[::-1, ...]

        if self.hflip:
            frame = frame[:, ::-1, :]

        if self.zoom != (0.0, 0.0, 1.0, 1.0):
            w, h = self.resolution
            xi, yi, xf, yf = self.zoom
            xi, xf = int(xi * w), int(xf * w)
            yi, yf = int(yi * h), int(yf * h)
            frame = frame[xi:xf, yi:yf, :]
        return frame

    def average(self, n=3):
        """Average n frames"""
        print(f"averaging over {n} frames")
        h, w = self.resolution
        stack = np.empty((w, h, 3, n))
        for i in range(n):
            stack[..., i] = self.data / n
        # BGR to RGB
        return stack.sum(axis=-1).astype(np.uint8)[..., ::-1]

    @property
    def data(self):
        return self.read()
