import cv2
import numpy as np
from pathlib import Path
from pyzjr.utils.check import is_file

def read_gray(filename):
    if not is_file(filename):
        raise ValueError(f"The file {filename} does not exist.")
    if isinstance(filename, Path):
        filename = str(filename.resolve())
    return cv2.imdecode(np.fromfile(filename, np.uint8), cv2.IMREAD_GRAYSCALE)

def read_bgr(filename):
    if not is_file(filename):
        raise ValueError(f"The file {filename} does not exist.")
    if isinstance(filename, Path):
        filename = str(filename.resolve())
    return cv2.imdecode(np.fromfile(filename, np.uint8), cv2.IMREAD_COLOR)

def read_rgb(filename):
    if not is_file(filename):
        raise ValueError(f"The file {filename} does not exist.")
    if isinstance(filename, Path):
        filename = str(filename.resolve())
    return cv2.imdecode(np.fromfile(filename, np.uint8), cv2.IMREAD_COLOR)[:, :, ::-1]