"""
Copyright (c) 2022, Auorui.
All rights reserved.
"""
import cv2
import numpy as np
from pathlib import Path
from urllib import request

from pyzjr.utils.check import is_numpy, is_list, is_url, is_pil
from pyzjr.utils.randfun import randstring

def imwriter(filename: str, img: np.ndarray, params=None):
    """Write the image to a file."""
    try:
        cv2.imencode(Path(filename).suffix, img, params)[1].tofile(filename)
        return True
    except Exception:
        return False

def display(imgArray, winname=None, scale=1.):
    """Displays an image in the specified window."""
    _imshow = cv2.imshow  # copy to avoid recursion errors
    if winname is None:
        winname = randstring(5)
    if is_numpy(imgArray):
        height, width = imgArray.shape[:2]
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(imgArray, (new_width, new_height))
        _imshow(winname.encode('unicode_escape').decode(), image)
    elif is_list(imgArray):
        image = StackedImagesV1(scale, imgArray)
        _imshow(winname.encode('unicode_escape').decode(), image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def url2image(url):
    """Same usage as cv2.imread()"""
    if is_url(url):
        res = request.urlopen(url, timeout=3)
    else:
        raise ValueError("The current input parameter does not conform to the URL format")
    try:
        image = np.asarray(bytearray(res.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
    except:
        print('Load read - Image timeout!')
        image = []
    h, w, c = image.shape
    if c == 4:
        image = image[:, :, :3]
    return image

def stacked2image(image1, image2, is_hstack=True):
    """Simply overlaying two images"""
    stack = np.hstack if is_hstack else np.vstack
    image = stack([image1, image2])
    return image

def StackedImagesV1(scale, imgArray):
    """
    Display Images According to List Structure

    :param scale: The scale of the images, where 1 represents the original size.
    :param imgArray: A list of images representing the arrangement in rows and columns.
    :return: A generated image that displays the images in the order specified by the input list, arranged in a grid.
    """
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver

def StackedImagesV2(scale, imgList, cols):
    """
    Combine multiple images into a single display within a single window
    :param scale: The scaling factor for the images, where a value greater than 1 indicates enlargement and a value less than 1 indicates reduction.
    :param imgList: A list of images to be combined.
    :param cols: The number of images to display per row.
    :return: The combined image.
    """
    totalImages = len(imgList)
    rows = totalImages // cols if totalImages // cols * cols == totalImages else totalImages // cols + 1
    blankImages = cols * rows - totalImages

    width = imgList[0].shape[1]
    height = imgList[0].shape[0]
    imgBlank = np.zeros((height, width, 3), np.uint8)
    imgList.extend([imgBlank] * blankImages)
    for i in range(cols * rows):
        imgList[i] = cv2.resize(imgList[i], (0, 0), None, scale, scale)
        if len(imgList[i].shape) == 2:
            imgList[i] = cv2.cvtColor(imgList[i], cv2.COLOR_GRAY2BGR)
    hor = [imgBlank] * rows
    for y in range(rows):
        line = []
        for x in range(cols):
            line.append(imgList[y * cols + x])
        hor[y] = np.hstack(line)
    ver = np.vstack(hor)
    return ver

def imattributes(image):
    """Retrieve image attributes"""
    if is_numpy(image):
        imshape = image.shape
        size = imshape[:2]
        dtype = image.dtype
        height, width = size

        if len(imshape) == 2:
            depth = image.itemsize * 8
        else:
            depth = image.itemsize * 8 * imshape[2]

        return {
            "shape": imshape,
            "size": size,
            "height": height,
            "width": width,
            "dtype": dtype,
            "depth": depth,
            "source": "NumPy"
        }
    elif is_pil(image):
        width, height = image.size
        mode = image.mode

        if mode == 'L':  # Grayscale
            depth = 8
        elif mode in ('RGB', 'RGBA'):
            depth = 8 * 3 if mode == 'RGB' else 8 * 4
        elif mode in ('I', 'F'):  # Integer or float (single channel)
            depth = image.getbands()[0].size * 8
        else:
            depth = "Unknown"  # Other modes are not handled here

        return {
            "shape": (height, width, len(image.getbands())),  # Simulate a NumPy shape
            "size": (width, height),
            "height": height,
            "width": width,
            "dtype": "PIL mode " + mode,  # PIL doesn't have a direct dtype equivalent
            "depth": depth,
            "source": "PIL"
        }
    else:
        return "Input is not a NumPy array or PIL Image."

if __name__ == "__main__":
    image_path = r"E:\PythonProject\pyzjrPyPi\pyzjr\test.png"
    image = cv2.imread(image_path)
    display(stacked2image(image, image))
    print(imattributes(image))