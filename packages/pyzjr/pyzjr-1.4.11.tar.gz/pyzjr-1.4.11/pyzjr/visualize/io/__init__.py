"""
Copyright (c) 2025, Auorui.
All rights reserved.

This module is used for reading and displaying images and videos. The image contains
OpenCV and PIL, and the loading method for the video is OpenCV.
"""
from .imvision import imwriter, display, url2image, stacked2image, \
    StackedImagesV1, StackedImagesV2, imattributes
from .pilvision import imshowplt, StackedpltV1, StackedpltV2, matplotlib_patch
from .videovision import VideoCap, Mp4toGif, FindColor, DetectImageColor, DetectVideoColor

from .ioread import read_bgr, read_gray, read_rgb

from .imtensor import (
    to_numpy,
    to_tensor,
    to_bchw,
    image_to_bchw,
    hwc2chw,
    chw2hwc,
    tensor_to_image,
    image_to_tensor,
    img2tensor,
    label2tensor,
    read_tensor,
    write_tensor
)