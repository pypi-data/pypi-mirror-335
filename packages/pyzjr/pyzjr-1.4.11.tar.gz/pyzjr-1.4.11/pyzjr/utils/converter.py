import cv2
import numpy as np
from PIL import Image
from itertools import repeat

from pyzjr.utils.check import is_Iterable

def _ntuple(n):
    def parse(x):
        if is_Iterable(x):
            return x
        return tuple(repeat(x, n))
    return parse

to_1tuple = _ntuple(1)
to_2tuple = _ntuple(2)
to_3tuple = _ntuple(3)
to_4tuple = _ntuple(4)
to_ntuple = _ntuple